import pytest
from apiflask import APIFlask
from marshmallow import ValidationError

from flask_tutorial.error_handlers import register_error_handlers
from flask_tutorial.errors import BusinessRuleError, ResourceNotFoundError


@pytest.fixture
def error_app():
    app = APIFlask(__name__)
    app.config["TESTING"] = True
    register_error_handlers(app)

    @app.get("/boom/not-found")
    def raise_not_found():
        raise ResourceNotFoundError("Category 42 not found")

    @app.get("/boom/validation")
    def raise_validation():
        raise ValidationError({"name": ["Missing data for required field."]})

    @app.get("/boom/business-rule")
    def raise_business_rule():
        raise BusinessRuleError("Cannot delete a category that still has products")

    @app.get("/boom/unexpected")
    def raise_unexpected():
        raise RuntimeError("kaboom")

    return app


@pytest.fixture
def error_client(error_app):
    return error_app.test_client()


def test_resource_not_found_maps_to_404(error_client):
    response = error_client.get("/boom/not-found")

    assert response.status_code == 404
    body = response.get_json()
    assert body["success"] is False
    assert body["message"] == "Category 42 not found"
    assert body["data"] is None


def test_validation_error_maps_to_400_with_field_errors(error_client):
    response = error_client.get("/boom/validation")

    assert response.status_code == 400
    body = response.get_json()
    assert body["success"] is False
    assert body["errors"] == {"name": ["Missing data for required field."]}


def test_business_rule_error_maps_to_422(error_client):
    response = error_client.get("/boom/business-rule")

    assert response.status_code == 422
    body = response.get_json()
    assert body["success"] is False
    assert body["message"] == "Cannot delete a category that still has products"


def test_unexpected_error_maps_to_500(error_client):
    response = error_client.get("/boom/unexpected")

    assert response.status_code == 500
    body = response.get_json()
    assert body["success"] is False
    assert body["data"] is None
