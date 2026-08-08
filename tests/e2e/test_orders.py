import pytest

from flask_tutorial.extensions import db
from flask_tutorial.models.category import Category
from flask_tutorial.models.customer import Customer
from flask_tutorial.models.order import Order
from flask_tutorial.models.product import Product


@pytest.fixture(autouse=True)
def clean_orders_table(app):
    with app.app_context():
        db.session.query(Order).delete()
        db.session.query(Product).delete()
        db.session.query(Category).delete()
        db.session.query(Customer).delete()
        db.session.commit()
    yield
    with app.app_context():
        db.session.query(Order).delete()
        db.session.query(Product).delete()
        db.session.query(Category).delete()
        db.session.query(Customer).delete()
        db.session.commit()


def _create_customer(client, admin_headers, email="ada@example.com") -> int:
    response = client.post(
        "/api/v1/customers",
        json={
            "first_name": "Ada",
            "last_name": "Lovelace",
            "telephone": "555-1234",
            "email": email,
            "address": "1 Analytical Way",
        },
        headers=admin_headers,
    )
    return response.get_json()["data"]["id"]


def _create_product(client, admin_headers) -> tuple[int, int]:
    category_response = client.post(
        "/api/v1/categories", json={"category_name": "Electronics"}, headers=admin_headers
    )
    category_id = category_response.get_json()["data"]["id"]
    product_response = client.post(
        "/api/v1/products",
        json={"category_id": category_id, "product_name": "Laptop", "unit_price": 100.0},
        headers=admin_headers,
    )
    return category_id, product_response.get_json()["data"]["id"]


def test_full_crud_lifecycle_and_computed_total(client, admin_headers):
    customer_id = _create_customer(client, admin_headers)
    _, product_id = _create_product(client, admin_headers)

    create_response = client.post(
        "/api/v1/orders",
        json={"customer_id": customer_id, "product_id": product_id, "quantity": 3},
        headers=admin_headers,
    )
    assert create_response.status_code == 201
    created = create_response.get_json()["data"]
    assert created["total"] == 300.0
    order_id = created["id"]

    detail_response = client.get(f"/api/v1/orders/{order_id}", headers=admin_headers)
    assert detail_response.status_code == 200
    assert detail_response.get_json()["data"]["quantity"] == 3

    update_response = client.put(
        f"/api/v1/orders/{order_id}",
        json={"customer_id": customer_id, "product_id": product_id, "quantity": 5},
        headers=admin_headers,
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["data"]["total"] == 500.0

    delete_response = client.delete(f"/api/v1/orders/{order_id}", headers=admin_headers)
    assert delete_response.status_code == 200

    after_delete_response = client.get(f"/api/v1/orders/{order_id}", headers=admin_headers)
    assert after_delete_response.status_code == 404


def test_customer_id_and_product_id_filters_on_the_list(client, admin_headers):
    customer_id = _create_customer(client, admin_headers)
    other_customer_id = _create_customer(client, admin_headers, email="grace@example.com")
    _, product_id = _create_product(client, admin_headers)

    client.post(
        "/api/v1/orders",
        json={"customer_id": customer_id, "product_id": product_id, "quantity": 1},
        headers=admin_headers,
    )
    client.post(
        "/api/v1/orders",
        json={"customer_id": other_customer_id, "product_id": product_id, "quantity": 2},
        headers=admin_headers,
    )

    response = client.get(f"/api/v1/orders?customer_id={customer_id}", headers=admin_headers)

    assert response.status_code == 200
    page = response.get_json()["data"]
    assert page["total_count"] == 1
    assert page["items"][0]["customer_id"] == customer_id


def test_create_with_unknown_customer_returns_404(client, admin_headers):
    _, product_id = _create_product(client, admin_headers)

    response = client.post(
        "/api/v1/orders",
        json={"customer_id": 999999, "product_id": product_id, "quantity": 1},
        headers=admin_headers,
    )

    assert response.status_code == 404
    assert response.get_json()["success"] is False


def test_create_with_unknown_product_returns_404(client, admin_headers):
    customer_id = _create_customer(client, admin_headers)

    response = client.post(
        "/api/v1/orders",
        json={"customer_id": customer_id, "product_id": 999999, "quantity": 1},
        headers=admin_headers,
    )

    assert response.status_code == 404
    assert response.get_json()["success"] is False


def test_list_without_authentication_returns_401(client):
    response = client.get("/api/v1/orders")

    assert response.status_code == 401
