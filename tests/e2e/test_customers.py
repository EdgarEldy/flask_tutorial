import pytest

from flask_tutorial.extensions import db
from flask_tutorial.models.customer import Customer


@pytest.fixture(autouse=True)
def clean_customers_table(app):
    with app.app_context():
        db.session.query(Customer).delete()
        db.session.commit()
    yield
    with app.app_context():
        db.session.query(Customer).delete()
        db.session.commit()


def _payload(**overrides):
    payload = {
        "first_name": "Ada",
        "last_name": "Lovelace",
        "telephone": "555-1234",
        "email": "ada@example.com",
        "address": "1 Analytical Way",
    }
    payload.update(overrides)
    return payload


def test_full_crud_lifecycle(client):
    create_response = client.post("/api/v1/customers", json=_payload())
    assert create_response.status_code == 201
    created = create_response.get_json()["data"]
    customer_id = created["id"]

    detail_response = client.get(f"/api/v1/customers/{customer_id}")
    assert detail_response.status_code == 200
    assert detail_response.get_json()["data"]["email"] == "ada@example.com"

    update_response = client.put(f"/api/v1/customers/{customer_id}", json=_payload(telephone="555-0000"))
    assert update_response.status_code == 200
    assert update_response.get_json()["data"]["telephone"] == "555-0000"

    delete_response = client.delete(f"/api/v1/customers/{customer_id}")
    assert delete_response.status_code == 200

    after_delete_response = client.get(f"/api/v1/customers/{customer_id}")
    assert after_delete_response.status_code == 404


def test_search_query_parameter(client):
    client.post("/api/v1/customers", json=_payload(first_name="Ada", email="ada@example.com"))
    client.post("/api/v1/customers", json=_payload(first_name="Grace", last_name="Hopper", email="grace@example.com"))

    response = client.get("/api/v1/customers?search=Ada")

    assert response.status_code == 200
    page = response.get_json()["data"]
    assert page["total_count"] == 1
    assert page["items"][0]["first_name"] == "Ada"


def test_create_with_missing_field_returns_400_with_field_errors(client):
    response = client.post("/api/v1/customers", json={"first_name": "Ada"})

    assert response.status_code == 400
    body = response.get_json()
    assert body["success"] is False
    assert "email" in body["errors"]["json"]


def test_create_with_duplicate_email_returns_422(client):
    client.post("/api/v1/customers", json=_payload())

    response = client.post("/api/v1/customers", json=_payload(first_name="Grace", last_name="Hopper"))

    assert response.status_code == 422
    assert response.get_json()["success"] is False
