from flask_tutorial.extensions import db


class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_tokens"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)
    token = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(255), nullable=False)
    expiry_date = db.Column(db.DateTime(timezone=True), nullable=False)

    user = db.relationship("User")
