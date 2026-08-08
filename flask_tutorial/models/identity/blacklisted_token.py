from datetime import datetime, timezone

from flask_tutorial.extensions import db


class BlacklistedToken(db.Model):
    __tablename__ = "blacklisted_tokens"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)
    token = db.Column(db.String(768), nullable=False)
    jti = db.Column(db.String(255), nullable=False, unique=True)
    blacklisted_at = db.Column(db.DateTime(timezone=True), nullable=True, default=lambda: datetime.now(timezone.utc))
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime(timezone=True), nullable=True)
    validated_at = db.Column(db.DateTime(timezone=True), nullable=True)

    user = db.relationship("User")
