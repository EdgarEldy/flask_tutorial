import pytest

from flask_tutorial.errors import BusinessRuleError
from flask_tutorial.services.customer_service import CustomerService


@pytest.fixture
def service():
    return CustomerService()


def test_create_raises_business_rule_error_on_duplicate_email(service, mocker):
    mocker.patch.object(CustomerService, "_email_taken", return_value=True)

    with pytest.raises(BusinessRuleError):
        service.create("Ada", "Lovelace", "555-1234", "ada@example.com", "1 Analytical Way")


def test_update_raises_business_rule_error_on_duplicate_email(service, mocker):
    mocker.patch.object(
        CustomerService,
        "get_by_id",
        return_value=mocker.Mock(id=1, first_name="Ada", last_name="Lovelace"),
    )
    mocker.patch.object(CustomerService, "_email_taken", return_value=True)

    with pytest.raises(BusinessRuleError):
        service.update(1, "Ada", "Lovelace", "555-0000", "grace@example.com", "1 Analytical Way")


def test_update_excludes_the_customer_being_updated_from_the_email_check(service, mocker):
    customer = mocker.Mock(id=1, first_name="Ada", last_name="Lovelace")
    mocker.patch.object(CustomerService, "get_by_id", return_value=customer)
    email_taken = mocker.patch.object(CustomerService, "_email_taken", return_value=False)
    mocker.patch("flask_tutorial.services.customer_service.db.session.commit")

    service.update(1, "Ada", "Lovelace", "555-0000", "ada@example.com", "1 Analytical Way")

    email_taken.assert_called_once_with("ada@example.com", exclude_id=1)
