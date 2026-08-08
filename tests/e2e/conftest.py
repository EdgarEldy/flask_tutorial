import pytest
from werkzeug.security import generate_password_hash

from flask_tutorial.extensions import db
from flask_tutorial.models.identity.permission import Permission
from flask_tutorial.models.identity.role import Role
from flask_tutorial.models.identity.user import User

ALL_RESOURCES = ["categories", "products", "customers", "orders"]
ALL_ACTIONS = ["create", "update", "delete"]
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "supersecret123"


@pytest.fixture
def admin_headers(app, client):
    """An Authorization header for a freshly-created Admin-role user with
    every create/update/delete permission - for feature/*'s existing e2e
    tests to authenticate against now-protected mutating endpoints."""
    with app.app_context():
        permissions = [Permission(resource=r, action=a) for r in ALL_RESOURCES for a in ALL_ACTIONS]
        admin_role = Role(role_name="Admin", permissions=permissions)
        admin = User(
            first_name="Admin",
            last_name="User",
            email=ADMIN_EMAIL,
            password=generate_password_hash(ADMIN_PASSWORD),
            enabled=True,
            account_locked=False,
            roles=[admin_role],
        )
        db.session.add(admin)
        db.session.commit()

    login_response = client.post("/api/v1/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    token = login_response.get_json()["data"]["access_token"]

    yield {"Authorization": f"Bearer {token}"}

    with app.app_context():
        db.session.execute(db.text("DELETE FROM role_user"))
        db.session.execute(db.text("DELETE FROM role_permission"))
        db.session.query(User).filter_by(email=ADMIN_EMAIL).delete()
        db.session.query(Role).filter_by(role_name="Admin").delete()
        db.session.query(Permission).delete()
        db.session.commit()
