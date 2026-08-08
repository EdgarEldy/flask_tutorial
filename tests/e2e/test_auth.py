import re

import pytest
from werkzeug.security import generate_password_hash

from flask_tutorial.extensions import db
from flask_tutorial.models.category import Category
from flask_tutorial.models.identity.activation_token import ActivationToken
from flask_tutorial.models.identity.blacklisted_token import BlacklistedToken
from flask_tutorial.models.identity.password_reset_token import PasswordResetToken
from flask_tutorial.models.identity.permission import Permission
from flask_tutorial.models.identity.role import Role
from flask_tutorial.models.identity.user import User
from flask_tutorial.services.auth_service import AuthService


class FakeEmailService:
    def __init__(self):
        self.sent = []

    def send(self, to, subject, html_body):
        self.sent.append({"to": to, "subject": subject, "html_body": html_body})


def _clean_identity_tables():
    db.session.query(BlacklistedToken).delete()
    db.session.query(PasswordResetToken).delete()
    db.session.query(ActivationToken).delete()
    db.session.execute(db.text("DELETE FROM role_user"))
    db.session.execute(db.text("DELETE FROM role_permission"))
    db.session.query(User).delete()
    db.session.query(Role).delete()
    db.session.query(Permission).delete()
    # test_role_based_access creates a real Category via the API.
    db.session.query(Category).delete()
    db.session.commit()


@pytest.fixture(autouse=True)
def clean_identity_tables(app):
    with app.app_context():
        _clean_identity_tables()
    yield
    with app.app_context():
        _clean_identity_tables()


@pytest.fixture
def fake_email_service():
    return FakeEmailService()


@pytest.fixture(autouse=True)
def use_fake_email_service(fake_email_service, monkeypatch):
    import flask_tutorial.blueprints.auth.views as auth_views

    monkeypatch.setattr(auth_views, "service", AuthService(email_service=fake_email_service))


def _extract_token(html_body: str) -> str:
    return re.search(r"token=([\w-]+)", html_body).group(1)


def _register_and_confirm(client, fake_email_service, email="ada@example.com") -> None:
    client.post(
        "/api/v1/auth/register",
        json={"first_name": "Ada", "last_name": "Lovelace", "email": email, "password": "supersecret123"},
    )
    token = _extract_token(fake_email_service.sent[-1]["html_body"])
    client.post("/api/v1/auth/confirm-email", json={"email": email, "token": token})


def test_register_confirm_login_flow(client, fake_email_service):
    register_response = client.post(
        "/api/v1/auth/register",
        json={"first_name": "Ada", "last_name": "Lovelace", "email": "ada@example.com", "password": "supersecret123"},
    )
    assert register_response.status_code == 201
    assert len(fake_email_service.sent) == 1

    login_before_confirm = client.post(
        "/api/v1/auth/login", json={"email": "ada@example.com", "password": "supersecret123"}
    )
    assert login_before_confirm.status_code == 422

    activation_token = _extract_token(fake_email_service.sent[-1]["html_body"])
    confirm_response = client.post(
        "/api/v1/auth/confirm-email", json={"email": "ada@example.com", "token": activation_token}
    )
    assert confirm_response.status_code == 200

    login_response = client.post(
        "/api/v1/auth/login", json={"email": "ada@example.com", "password": "supersecret123"}
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.get_json()["data"]


def test_forgot_password_reset_password_login_flow(client, fake_email_service):
    _register_and_confirm(client, fake_email_service)

    fake_email_service.sent.clear()
    forgot_response = client.post("/api/v1/auth/forgot-password", json={"email": "ada@example.com"})
    assert forgot_response.status_code == 200

    reset_token = _extract_token(fake_email_service.sent[-1]["html_body"])
    reset_response = client.post(
        "/api/v1/auth/reset-password",
        json={"email": "ada@example.com", "token": reset_token, "new_password": "newpassword456"},
    )
    assert reset_response.status_code == 200

    reuse_response = client.post(
        "/api/v1/auth/reset-password",
        json={"email": "ada@example.com", "token": reset_token, "new_password": "another123"},
    )
    assert reuse_response.status_code == 404

    login_response = client.post(
        "/api/v1/auth/login", json={"email": "ada@example.com", "password": "newpassword456"}
    )
    assert login_response.status_code == 200


def test_logout_revokes_the_token(client, fake_email_service):
    _register_and_confirm(client, fake_email_service)
    login_response = client.post(
        "/api/v1/auth/login", json={"email": "ada@example.com", "password": "supersecret123"}
    )
    headers = {"Authorization": f"Bearer {login_response.get_json()['data']['access_token']}"}

    assert client.get("/api/v1/auth/me", headers=headers).status_code == 200

    logout_response = client.post("/api/v1/auth/logout", headers=headers)
    assert logout_response.status_code == 200

    after_logout_response = client.get("/api/v1/auth/me", headers=headers)
    assert after_logout_response.status_code == 401


def test_role_based_access(app, client, fake_email_service):
    with app.app_context():
        create_categories_permission = Permission(resource="categories", action="create")
        db.session.add(Role(role_name="Admin", permissions=[create_categories_permission]))
        db.session.add(Role(role_name="User"))
        db.session.commit()

    _register_and_confirm(client, fake_email_service, email="grace@example.com")
    user_login = client.post(
        "/api/v1/auth/login", json={"email": "grace@example.com", "password": "supersecret123"}
    )
    user_headers = {"Authorization": f"Bearer {user_login.get_json()['data']['access_token']}"}

    forbidden_response = client.post(
        "/api/v1/categories", json={"category_name": "Electronics"}, headers=user_headers
    )
    assert forbidden_response.status_code == 403

    with app.app_context():
        admin_role = Role.query.filter_by(role_name="Admin").first()
        admin = User(
            first_name="Ada",
            last_name="Lovelace",
            email="admin@example.com",
            password=generate_password_hash("supersecret123"),
            enabled=True,
            account_locked=False,
            roles=[admin_role],
        )
        db.session.add(admin)
        db.session.commit()

    admin_login = client.post(
        "/api/v1/auth/login", json={"email": "admin@example.com", "password": "supersecret123"}
    )
    admin_headers = {"Authorization": f"Bearer {admin_login.get_json()['data']['access_token']}"}

    allowed_response = client.post(
        "/api/v1/categories", json={"category_name": "Electronics"}, headers=admin_headers
    )
    assert allowed_response.status_code == 201

    unauthenticated_response = client.get("/api/v1/customers")
    assert unauthenticated_response.status_code == 401
