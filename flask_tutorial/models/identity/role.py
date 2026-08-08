from flask_tutorial.extensions import db

role_user = db.Table(
    "role_user",
    db.Column("user_id", db.BigInteger, db.ForeignKey("users.id"), primary_key=True),
    db.Column("role_id", db.BigInteger, db.ForeignKey("roles.id"), primary_key=True),
)

role_permission = db.Table(
    "role_permission",
    db.Column("role_id", db.BigInteger, db.ForeignKey("roles.id"), primary_key=True),
    db.Column("permission_id", db.BigInteger, db.ForeignKey("permissions.id"), primary_key=True),
)


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    role_name = db.Column(db.String(50), nullable=False, unique=True)

    users = db.relationship("User", secondary=role_user, back_populates="roles")
    permissions = db.relationship("Permission", secondary=role_permission, back_populates="roles")
