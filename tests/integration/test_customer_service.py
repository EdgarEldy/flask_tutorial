import pytest
from sqlalchemy.exc import IntegrityError

from flask_tutorial.errors import BusinessRuleError
from flask_tutorial.extensions import db
from flask_tutorial.models.customer import Customer
from flask_tutorial.services.customer_service import CustomerService


@pytest.fixture
def service():
    return CustomerService()


def test_get_all_searches_by_first_or_last_name(app, service):
    with app.app_context():
        service.create("Ada", "Lovelace", "555-1234", "ada@example.com", "1 Analytical Way")
        service.create("Grace", "Hopper", "555-5678", "grace@example.com", "COBOL Ln")
        service.create("Alan", "Turing", "555-0000", "alan@example.com", "Enigma St")

        page_response = service.get_all(page=1, page_size=10, search="ada")

        assert page_response.total_count == 1
        assert page_response.items[0].last_name == "Lovelace"


def test_create_raises_business_rule_error_on_duplicate_email(app, service):
    with app.app_context():
        service.create("Ada", "Lovelace", "555-1234", "ada@example.com", "1 Analytical Way")

        with pytest.raises(BusinessRuleError):
            service.create("Grace", "Hopper", "555-5678", "ada@example.com", "COBOL Ln")


def test_update_allows_keeping_the_same_email(app, service):
    with app.app_context():
        customer = service.create("Ada", "Lovelace", "555-1234", "ada@example.com", "1 Analytical Way")

        updated = service.update(
            customer.id, "Ada", "Lovelace", "555-0000", "ada@example.com", "1 Analytical Way"
        )

        assert updated.telephone == "555-0000"


def test_update_raises_business_rule_error_when_email_belongs_to_another_customer(app, service):
    with app.app_context():
        service.create("Ada", "Lovelace", "555-1234", "ada@example.com", "1 Analytical Way")
        grace = service.create("Grace", "Hopper", "555-5678", "grace@example.com", "COBOL Ln")

        with pytest.raises(BusinessRuleError):
            service.update(grace.id, "Grace", "Hopper", "555-5678", "ada@example.com", "COBOL Ln")


def test_email_unique_constraint_is_enforced_by_the_database(app):
    with app.app_context():
        db.session.add(
            Customer(
                first_name="Ada",
                last_name="Lovelace",
                telephone="555-1234",
                email="ada@example.com",
                address="1 Analytical Way",
            )
        )
        db.session.commit()

        db.session.add(
            Customer(
                first_name="Grace",
                last_name="Hopper",
                telephone="555-5678",
                email="ada@example.com",
                address="COBOL Ln",
            )
        )
        with pytest.raises(IntegrityError):
            db.session.commit()
