import secrets
from datetime import datetime, timedelta, timezone

from flask import current_app
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash

from flask_tutorial.errors import BusinessRuleError, ResourceNotFoundError
from flask_tutorial.extensions import db
from flask_tutorial.models.identity.activation_token import ActivationToken
from flask_tutorial.models.identity.blacklisted_token import BlacklistedToken
from flask_tutorial.models.identity.password_reset_token import PasswordResetToken
from flask_tutorial.models.identity.role import Role
from flask_tutorial.models.identity.user import User
from flask_tutorial.services.email_service import EmailService

ACTIVATION_TOKEN_TTL = timedelta(hours=24)
PASSWORD_RESET_TOKEN_TTL = timedelta(hours=1)
PASSWORD_RESET_TOKEN_TYPE = "password_reset"
DEFAULT_ROLE_NAME = "User"


class AuthService:
    def __init__(self, email_service: EmailService | None = None):
        self.email_service = email_service or EmailService()

    def register(self, first_name: str, last_name: str, email: str, password: str) -> User:
        if self._email_registered(email):
            raise BusinessRuleError(f"Email {email} is already in use")

        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=generate_password_hash(password),
            enabled=False,
            account_locked=False,
        )
        default_role = Role.query.filter_by(role_name=DEFAULT_ROLE_NAME).first()
        if default_role is not None:
            user.roles.append(default_role)
        db.session.add(user)
        db.session.commit()

        self._issue_activation_email(user)
        return user

    def confirm_email(self, token: str) -> None:
        activation_token = ActivationToken.query.filter_by(token=token).first()
        if activation_token is None:
            raise ResourceNotFoundError("Invalid activation token")
        if activation_token.validated_at is not None:
            raise BusinessRuleError("Activation token has already been used")
        if activation_token.expires_at is not None and activation_token.expires_at < datetime.now(timezone.utc):
            raise BusinessRuleError("Activation token has expired")

        user = db.session.get(User, activation_token.user_id)
        user.enabled = True
        activation_token.validated_at = datetime.now(timezone.utc)
        db.session.commit()

    def resend_confirmation(self, email: str) -> None:
        user = self._find_user_by_email(email)
        if user is not None and not user.enabled:
            self._issue_activation_email(user)
        # Same (no) response either way - never leak whether the account exists.

    def login(self, email: str, password: str) -> str:
        user = self._find_user_by_email(email)
        if user is None:
            raise BusinessRuleError("Invalid email or password")
        if not user.enabled:
            raise BusinessRuleError("Account is not activated")
        if user.account_locked:
            raise BusinessRuleError("Account is locked")
        if not check_password_hash(user.password, password):
            raise BusinessRuleError("Invalid email or password")

        return create_access_token(
            identity=str(user.id), additional_claims={"permissions": self._resolve_permissions(user)}
        )

    def get_current_user(self) -> User:
        user_id = int(get_jwt_identity())
        user = db.session.get(User, user_id)
        if user is None:
            raise ResourceNotFoundError(f"User {user_id} not found")
        return user

    def logout(self, raw_token: str) -> None:
        claims = get_jwt()
        db.session.add(
            BlacklistedToken(
                user_id=int(get_jwt_identity()),
                token=raw_token,
                jti=claims["jti"],
                blacklisted_at=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc),
                expires_at=datetime.fromtimestamp(claims["exp"], tz=timezone.utc),
            )
        )
        db.session.commit()

    def forgot_password(self, email: str) -> None:
        user = self._find_user_by_email(email)
        if user is not None:
            self._issue_password_reset_email(user)
        # Always the same (no) response, whether or not the account exists.

    def reset_password(self, token: str, new_password: str) -> None:
        reset_token = PasswordResetToken.query.filter_by(token=token).first()
        if reset_token is None:
            raise ResourceNotFoundError("Invalid password reset token")
        if reset_token.expiry_date < datetime.now(timezone.utc):
            raise BusinessRuleError("Password reset token has expired")

        user = db.session.get(User, reset_token.user_id)
        user.password = generate_password_hash(new_password)
        # Deleted, not flagged: this table has no "used" column - consuming
        # the row is what makes a reused token subsequently look invalid.
        db.session.delete(reset_token)
        db.session.commit()

    def _issue_activation_email(self, user: User) -> None:
        token = ActivationToken(
            user_id=user.id,
            token=secrets.token_urlsafe(32),
            expires_at=datetime.now(timezone.utc) + ACTIVATION_TOKEN_TTL,
        )
        db.session.add(token)
        db.session.commit()

        link = f"{current_app.config['FRONTEND_URL']}/confirm-email?token={token.token}"
        self.email_service.send(
            user.email, "Confirm your account", f'<p>Click to confirm your account: <a href="{link}">{link}</a></p>'
        )

    def _issue_password_reset_email(self, user: User) -> None:
        token = PasswordResetToken(
            user_id=user.id,
            token=secrets.token_urlsafe(32),
            type=PASSWORD_RESET_TOKEN_TYPE,
            expiry_date=datetime.now(timezone.utc) + PASSWORD_RESET_TOKEN_TTL,
        )
        db.session.add(token)
        db.session.commit()

        link = f"{current_app.config['FRONTEND_URL']}/reset-password?token={token.token}"
        self.email_service.send(
            user.email, "Reset your password", f'<p>Click to reset your password: <a href="{link}">{link}</a></p>'
        )

    @staticmethod
    def _resolve_permissions(user: User) -> list[str]:
        permissions = {f"{p.resource}:{p.action}" for role in user.roles for p in role.permissions}
        return sorted(permissions)

    @staticmethod
    def _email_registered(email: str) -> bool:
        return db.session.query(User.query.filter_by(email=email).exists()).scalar()

    @staticmethod
    def _find_user_by_email(email: str) -> User | None:
        return User.query.filter_by(email=email).first()
