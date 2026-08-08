from flask_tutorial.extensions import db


class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    telephone = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    address = db.Column(db.String(255), nullable=False)
