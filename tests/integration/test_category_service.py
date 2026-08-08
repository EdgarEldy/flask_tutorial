import pytest
from sqlalchemy.exc import IntegrityError

from flask_tutorial.errors import BusinessRuleError
from flask_tutorial.extensions import db
from flask_tutorial.models.category import Category
from flask_tutorial.models.product import Product
from flask_tutorial.services.category_service import CategoryService


@pytest.fixture
def service():
    return CategoryService()


def test_get_all_returns_the_right_page_and_total_count(app, service):
    with app.app_context():
        for i in range(5):
            db.session.add(Category(category_name=f"Category {i}"))
        db.session.commit()

        page_response = service.get_all(page=2, page_size=2)

        assert page_response.total_count == 5
        assert page_response.total_pages == 3
        assert [c.category_name for c in page_response.items] == ["Category 2", "Category 3"]


def test_create_persists_the_category(app, service):
    with app.app_context():
        category = service.create("Books")

        assert category.id is not None
        assert db.session.get(Category, category.id).category_name == "Books"


def test_update_persists_the_new_name(app, service):
    with app.app_context():
        category = service.create("Books")

        updated = service.update(category.id, "Books & Comics")

        assert updated.category_name == "Books & Comics"
        assert db.session.get(Category, category.id).category_name == "Books & Comics"


def test_delete_removes_the_category(app, service):
    with app.app_context():
        category = service.create("Books")

        service.delete(category.id)

        assert db.session.get(Category, category.id) is None


def test_category_name_not_null_constraint_is_enforced_by_the_database(app):
    with app.app_context():
        db.session.add(Category(category_name=None))
        with pytest.raises(IntegrityError):
            db.session.commit()


def test_delete_raises_business_rule_error_when_category_still_has_products(app, service):
    with app.app_context():
        category = service.create("Electronics")
        db.session.add(Product(category_id=category.id, product_name="Laptop", unit_price=999.99))
        db.session.commit()

        with pytest.raises(BusinessRuleError):
            service.delete(category.id)

        assert db.session.get(Category, category.id) is not None
