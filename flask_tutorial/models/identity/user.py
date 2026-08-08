from flask_tutorial.extensions import db
from flask_tutorial.models.identity.role import role_user


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    enabled = db.Column(db.Boolean, nullable=False, default=False)
    account_locked = db.Column(db.Boolean, nullable=False, default=False)

    roles = db.relationship("Role", secondary=role_user, back_populates="users")
