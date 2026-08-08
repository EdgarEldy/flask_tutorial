from flask_tutorial.extensions import db


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    category_name = db.Column(db.String(255), nullable=False)

    products = db.relationship("Product", back_populates="category")
