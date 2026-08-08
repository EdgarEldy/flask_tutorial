from datetime import datetime, timedelta, timezone

import pytest
from flask_jwt_extended import create_access_token, decode_token

from flask_tutorial.errors import BusinessRuleError, ResourceNotFoundError
from flask_tutorial.extensions import db
from flask_tutorial.models.identity.blacklisted_token import BlacklistedToken
from flask_tutorial.models.identity.password_reset_token import PasswordResetToken
from flask_tutorial.models.identity.permission import Permission
from flask_tutorial.models.identity.role import Role
from flask_tutorial.models.identity.user import User
from flask_tutorial.services.auth_service import AuthService


@pytest.fixture
def service(mocker):
    return AuthService(email_service=mocker.Mock())


def test_register_persists_the_user_disabled(app, service):
    with app.app_context():
        user = service.register("Ada", "Lovelace", "ada@example.com", "supersecret123")

        persisted = db.session.get(User, user.id)
        assert persisted.enabled is False
        assert persisted.password != "supersecret123"


def test_role_and_permission_assignment_persists(app):
    with app.app_context():
        permission = Permission(resource="categories", action="create")
        role = Role(role_name="Admin", permissions=[permission])
        user = User(
            first_name="Ada",
            last_name="Lovelace",
            email="ada@example.com",
            password="hashed",
            enabled=True,
            account_locked=False,
            roles=[role],
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id

        db.session.expire_all()
        reloaded = db.session.get(User, user_id)
        assert [r.role_name for r in reloaded.roles] == ["Admin"]
        assert [(p.resource, p.action) for p in reloaded.roles[0].permissions] == [("categories", "create")]


def test_reset_password_rejects_an_expired_token(app, service):
    with app.app_context():
        user = User(
            first_name="Ada",
            last_name="Lovelace",
            email="ada@example.com",
            password="hashed",
            enabled=True,
            account_locked=False,
        )
        db.session.add(user)
        db.session.commit()

        expired_token = PasswordResetToken(
            user_id=user.id,
            token="expired-token",
            type="password_reset",
            expiry_date=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        db.session.add(expired_token)
        db.session.commit()

        with pytest.raises(BusinessRuleError):
            service.reset_password("expired-token", "newpassword123")


def test_reset_password_rejects_an_already_used_token(app, service):
    with app.app_context():
        user = User(
            first_name="Ada",
            last_name="Lovelace",
            email="ada@example.com",
            password="hashed",
            enabled=True,
            account_locked=False,
        )
        db.session.add(user)
        db.session.commit()

        reset_token = PasswordResetToken(
            user_id=user.id,
            token="reusable-token",
            type="password_reset",
            expiry_date=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        db.session.add(reset_token)
        db.session.commit()

        service.reset_password("reusable-token", "newpassword123")

        with pytest.raises(ResourceNotFoundError):
            service.reset_password("reusable-token", "another-password")


def test_a_test_jwt_is_accepted_then_rejected_once_blacklisted(app):
    with app.app_context():
        user = User(
            first_name="Ada",
            last_name="Lovelace",
            email="ada@example.com",
            password="hashed",
            enabled=True,
            account_locked=False,
        )
        db.session.add(user)
        db.session.commit()

        token = create_access_token(identity=str(user.id), additional_claims={"permissions": []})
        headers = {"Authorization": f"Bearer {token}"}
        client = app.test_client()

        accepted_response = client.get("/api/v1/auth/me", headers=headers)
        assert accepted_response.status_code == 200

        jti = decode_token(token)["jti"]
        db.session.add(
            BlacklistedToken(
                user_id=user.id,
                token=token,
                jti=jti,
                blacklisted_at=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc),
                expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            )
        )
        db.session.commit()

        rejected_response = client.get("/api/v1/auth/me", headers=headers)
        assert rejected_response.status_code == 401
