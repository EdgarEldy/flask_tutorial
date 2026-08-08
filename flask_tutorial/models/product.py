from flask_tutorial.extensions import db


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    category_id = db.Column(db.BigInteger, db.ForeignKey("categories.id"), nullable=False)
    product_name = db.Column(db.String(255), nullable=False)
    unit_price = db.Column(db.Float, nullable=False)

    category = db.relationship("Category", back_populates="products")
