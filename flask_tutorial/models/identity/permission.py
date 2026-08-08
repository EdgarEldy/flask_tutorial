from flask_tutorial.extensions import db
from flask_tutorial.models.identity.role import role_permission


class Permission(db.Model):
    __tablename__ = "permissions"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    resource = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(50), nullable=False)

    roles = db.relationship("Role", secondary=role_permission, back_populates="permissions")
