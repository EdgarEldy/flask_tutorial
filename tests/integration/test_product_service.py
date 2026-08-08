import pytest
from sqlalchemy.exc import IntegrityError

from flask_tutorial.errors import ResourceNotFoundError
from flask_tutorial.extensions import db
from flask_tutorial.models.category import Category
from flask_tutorial.models.product import Product
from flask_tutorial.services.product_service import ProductService


@pytest.fixture
def service():
    return ProductService()


@pytest.fixture
def category_id(app) -> int:
    with app.app_context():
        cat = Category(category_name="Electronics")
        db.session.add(cat)
        db.session.commit()
        return cat.id


def test_get_all_filters_by_category_id(app, service, category_id):
    with app.app_context():
        other_category = Category(category_name="Books")
        db.session.add(other_category)
        db.session.commit()

        db.session.add(Product(category_id=category_id, product_name="Laptop", unit_price=999.99))
        db.session.add(Product(category_id=category_id, product_name="Mouse", unit_price=19.99))
        db.session.add(Product(category_id=other_category.id, product_name="Novel", unit_price=9.99))
        db.session.commit()

        page_response = service.get_all(page=1, page_size=10, category_id=category_id)

        assert page_response.total_count == 2
        assert {p.product_name for p in page_response.items} == {"Laptop", "Mouse"}


def test_get_all_paginates_without_a_category_filter(app, service, category_id):
    with app.app_context():
        for i in range(3):
            db.session.add(Product(category_id=category_id, product_name=f"Product {i}", unit_price=1.0))
        db.session.commit()

        page_response = service.get_all(page=1, page_size=2)

        assert page_response.total_count == 3
        assert len(page_response.items) == 2


def test_create_persists_and_loads_the_category_relationship(app, service, category_id):
    with app.app_context():
        product = service.create(category_id, "Laptop", 999.99)

        assert product.id is not None
        assert product.category.category_name == "Electronics"


def test_create_raises_resource_not_found_for_an_unknown_category(app, service):
    with app.app_context(), pytest.raises(ResourceNotFoundError):
        service.create(999999, "Laptop", 999.99)


def test_category_id_foreign_key_constraint_is_enforced_by_the_database(app):
    with app.app_context():
        db.session.add(Product(category_id=999999, product_name="Laptop", unit_price=999.99))
        with pytest.raises(IntegrityError):
            db.session.commit()
