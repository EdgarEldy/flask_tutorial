import pytest

from flask_tutorial.errors import ResourceNotFoundError
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
