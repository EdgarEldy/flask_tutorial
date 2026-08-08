from sqlalchemy.orm import joinedload

from flask_tutorial.errors import ResourceNotFoundError
from flask_tutorial.extensions import db
from flask_tutorial.models.customer import Customer
from flask_tutorial.models.order import Order
from flask_tutorial.models.product import Product
from flask_tutorial.schemas.common import PageResponse


class OrderService:
    def get_all(
        self, page: int, page_size: int, customer_id: int | None = None, product_id: int | None = None
    ) -> PageResponse[Order]:
        query = Order.query.options(joinedload(Order.customer), joinedload(Order.product))
        if customer_id is not None:
            query = query.filter(Order.customer_id == customer_id)
        if product_id is not None:
            query = query.filter(Order.product_id == product_id)
        query = query.order_by(Order.id)
        total_count = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return PageResponse(items=items, page=page, page_size=page_size, total_count=total_count)

    def get_by_id(self, order_id: int) -> Order:
        order = (
            Order.query.options(joinedload(Order.customer), joinedload(Order.product))
            .filter(Order.id == order_id)
            .first()
        )
        if order is None:
            raise ResourceNotFoundError(f"Order {order_id} not found")
        return order

    def create(self, customer_id: int, product_id: int, quantity: int) -> Order:
        self._get_customer_or_404(customer_id)
        product = self._get_product_or_404(product_id)
        order = Order(
            customer_id=customer_id,
            product_id=product_id,
            quantity=quantity,
            total=self._compute_total(quantity, product.unit_price),
        )
        db.session.add(order)
        db.session.commit()
        return order

    def update(self, order_id: int, customer_id: int, product_id: int, quantity: int) -> Order:
        order = self.get_by_id(order_id)
        self._get_customer_or_404(customer_id)
        product = self._get_product_or_404(product_id)
        order.customer_id = customer_id
        order.product_id = product_id
        order.quantity = quantity
        order.total = self._compute_total(quantity, product.unit_price)
        db.session.commit()
        return order

    def delete(self, order_id: int) -> None:
        order = self.get_by_id(order_id)
        db.session.delete(order)
        db.session.commit()

    @staticmethod
    def _compute_total(quantity: int, unit_price: float) -> float:
        return quantity * unit_price

    @staticmethod
    def _get_customer_or_404(customer_id: int) -> Customer:
        customer = db.session.get(Customer, customer_id)
        if customer is None:
            raise ResourceNotFoundError(f"Customer {customer_id} not found")
        return customer

    @staticmethod
    def _get_product_or_404(product_id: int) -> Product:
        product = db.session.get(Product, product_id)
        if product is None:
            raise ResourceNotFoundError(f"Product {product_id} not found")
        return product
