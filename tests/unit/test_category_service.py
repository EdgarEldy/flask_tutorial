import pytest

from flask_tutorial.errors import BusinessRuleError, ResourceNotFoundError
from flask_tutorial.models.category import Category
from flask_tutorial.services.category_service import CategoryService


@pytest.fixture
def service():
    return CategoryService()


def test_get_by_id_raises_resource_not_found_for_an_unknown_id(service, mocker):
    mocker.patch("flask_tutorial.services.category_service.db.session.get", return_value=None)

    with pytest.raises(ResourceNotFoundError):
        service.get_by_id(999)


def test_update_raises_resource_not_found_for_an_unknown_id(service, mocker):
    mocker.patch("flask_tutorial.services.category_service.db.session.get", return_value=None)

    with pytest.raises(ResourceNotFoundError):
        service.update(999, "Books")


def test_delete_raises_resource_not_found_for_an_unknown_id(service, mocker):
    mocker.patch("flask_tutorial.services.category_service.db.session.get", return_value=None)

    with pytest.raises(ResourceNotFoundError):
        service.delete(999)


def test_delete_raises_business_rule_error_when_category_still_has_products(service, mocker):
    mocker.patch(
        "flask_tutorial.services.category_service.db.session.get",
        return_value=Category(id=1, category_name="Books"),
    )
    mocker.patch.object(CategoryService, "_category_has_products", return_value=True)

    with pytest.raises(BusinessRuleError):
        service.delete(1)
