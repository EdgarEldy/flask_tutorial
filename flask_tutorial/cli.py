from flask_tutorial.extensions import db
from flask_tutorial.models.identity.permission import Permission
from flask_tutorial.models.identity.role import Role

WRITE_RESOURCES = ["categories", "products", "customers", "orders"]
WRITE_ACTIONS = ["create", "update", "delete"]
READ_ONLY_RESOURCES = ["categories", "products"]


def register_cli(app):
    @app.cli.command("seed-roles")
    def seed_roles():
        """Seed the default Admin (all permissions) and User (read-only
        categories/products) roles - safe to run more than once."""
        permissions = []
        for resource in WRITE_RESOURCES:
            for action in WRITE_ACTIONS:
                permissions.append(_get_or_create_permission(resource, action))
        read_only_permissions = [_get_or_create_permission(resource, "read") for resource in READ_ONLY_RESOURCES]
        db.session.flush()

        admin_role = Role.query.filter_by(role_name="Admin").first() or Role(role_name="Admin")
        admin_role.permissions = permissions + read_only_permissions
        db.session.add(admin_role)

        user_role = Role.query.filter_by(role_name="User").first() or Role(role_name="User")
        user_role.permissions = read_only_permissions
        db.session.add(user_role)

        db.session.commit()
        print(f"Seeded roles: Admin ({len(admin_role.permissions)} permissions), User ({len(user_role.permissions)} permissions)")


def _get_or_create_permission(resource: str, action: str) -> Permission:
    permission = Permission.query.filter_by(resource=resource, action=action).first()
    if permission is None:
        permission = Permission(resource=resource, action=action)
        db.session.add(permission)
    return permission
