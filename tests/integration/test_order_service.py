import pytest

from flask_tutorial.errors import ResourceNotFoundError
from flask_tutorial.extensions import db
from flask_tutorial.models.category import Category
from flask_tutorial.models.customer import Customer
from flask_tutorial.models.product import Product
from flask_tutorial.services.order_service import OrderService


@pytest.fixture
def service():
    return OrderService()


@pytest.fixture
def customer_id(app) -> int:
    with app.app_context():
        customer = Customer(
            first_name="Ada",
            last_name="Lovelace",
            telephone="555-1234",
            email="ada@example.com",
            address="1 Analytical Way",
        )
        db.session.add(customer)
        db.session.commit()
        return customer.id


@pytest.fixture
def product_id(app) -> int:
    with app.app_context():
        category = Category(category_name="Electronics")
        db.session.add(category)
        db.session.commit()
        product = Product(category_id=category.id, product_name="Laptop", unit_price=100.0)
        db.session.add(product)
        db.session.commit()
        return product.id


def test_create_computes_and_persists_the_total(app, service, customer_id, product_id):
    with app.app_context():
        order = service.create(customer_id, product_id, 3)

        assert order.total == 300.0


def test_update_recomputes_the_total_when_quantity_changes(app, service, customer_id, product_id):
    with app.app_context():
        order = service.create(customer_id, product_id, 3)

        updated = service.update(order.id, customer_id, product_id, 5)

        assert updated.total == 500.0


def test_create_raises_resource_not_found_for_an_unknown_customer(app, service, product_id):
    with app.app_context(), pytest.raises(ResourceNotFoundError):
        service.create(999999, product_id, 1)


def test_create_raises_resource_not_found_for_an_unknown_product(app, service, customer_id):
    with app.app_context(), pytest.raises(ResourceNotFoundError):
        service.create(customer_id, 999999, 1)


def test_get_by_id_eager_loads_customer_and_product(app, service, customer_id, product_id):
    with app.app_context():
        order = service.create(customer_id, product_id, 2)

        fetched = service.get_by_id(order.id)

        assert fetched.customer.first_name == "Ada"
        assert fetched.product.product_name == "Laptop"


def test_get_all_filters_by_customer_id_and_product_id(app, service, customer_id, product_id):
    with app.app_context():
        service.create(customer_id, product_id, 1)

        other_customer = Customer(
            first_name="Grace",
            last_name="Hopper",
            telephone="555-5678",
            email="grace@example.com",
            address="COBOL Ln",
        )
        db.session.add(other_customer)
        db.session.commit()
        service.create(other_customer.id, product_id, 2)

        page_response = service.get_all(page=1, page_size=10, customer_id=customer_id)

        assert page_response.total_count == 1
        assert page_response.items[0].customer_id == customer_id
