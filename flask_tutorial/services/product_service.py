from flask_tutorial.errors import ResourceNotFoundError
from flask_tutorial.extensions import db
from flask_tutorial.models.category import Category
from flask_tutorial.models.product import Product
from flask_tutorial.schemas.common import PageResponse


class ProductService:
    def get_all(self, page: int, page_size: int, category_id: int | None = None) -> PageResponse[Product]:
        query = Product.query
        if category_id is not None:
            query = query.filter(Product.category_id == category_id)
        query = query.order_by(Product.id)
        total_count = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return PageResponse(items=items, page=page, page_size=page_size, total_count=total_count)

    def get_by_id(self, product_id: int) -> Product:
        product = db.session.get(Product, product_id)
        if product is None:
            raise ResourceNotFoundError(f"Product {product_id} not found")
        return product

    def create(self, category_id: int, product_name: str, unit_price: float) -> Product:
        if db.session.get(Category, category_id) is None:
            raise ResourceNotFoundError(f"Category {category_id} not found")
        product = Product(category_id=category_id, product_name=product_name, unit_price=unit_price)
        db.session.add(product)
        db.session.commit()
        return product

    def update(self, product_id: int, category_id: int, product_name: str, unit_price: float) -> Product:
        product = self.get_by_id(product_id)
        if db.session.get(Category, category_id) is None:
            raise ResourceNotFoundError(f"Category {category_id} not found")
        product.category_id = category_id
        product.product_name = product_name
        product.unit_price = unit_price
        db.session.commit()
        return product

    def delete(self, product_id: int) -> None:
        product = self.get_by_id(product_id)
        db.session.delete(product)
        db.session.commit()
