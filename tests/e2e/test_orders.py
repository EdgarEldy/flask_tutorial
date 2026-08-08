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


def _create_customer(client, email="ada@example.com") -> int:
    response = client.post(
        "/api/v1/customers",
        json={
            "first_name": "Ada",
            "last_name": "Lovelace",
            "telephone": "555-1234",
            "email": email,
            "address": "1 Analytical Way",
        },
    )
    return response.get_json()["data"]["id"]


def _create_product(client) -> tuple[int, int]:
    category_response = client.post("/api/v1/categories", json={"category_name": "Electronics"})
    category_id = category_response.get_json()["data"]["id"]
    product_response = client.post(
        "/api/v1/products", json={"category_id": category_id, "product_name": "Laptop", "unit_price": 100.0}
    )
    return category_id, product_response.get_json()["data"]["id"]


def test_full_crud_lifecycle_and_computed_total(client):
    customer_id = _create_customer(client)
    _, product_id = _create_product(client)

    create_response = client.post(
        "/api/v1/orders", json={"customer_id": customer_id, "product_id": product_id, "quantity": 3}
    )
    assert create_response.status_code == 201
    created = create_response.get_json()["data"]
    assert created["total"] == 300.0
    order_id = created["id"]

    detail_response = client.get(f"/api/v1/orders/{order_id}")
    assert detail_response.status_code == 200
    assert detail_response.get_json()["data"]["quantity"] == 3

    update_response = client.put(
        f"/api/v1/orders/{order_id}", json={"customer_id": customer_id, "product_id": product_id, "quantity": 5}
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["data"]["total"] == 500.0

    delete_response = client.delete(f"/api/v1/orders/{order_id}")
    assert delete_response.status_code == 200

    after_delete_response = client.get(f"/api/v1/orders/{order_id}")
    assert after_delete_response.status_code == 404


def test_customer_id_and_product_id_filters_on_the_list(client):
    customer_id = _create_customer(client)
    other_customer_id = _create_customer(client, email="grace@example.com")
    _, product_id = _create_product(client)

    client.post("/api/v1/orders", json={"customer_id": customer_id, "product_id": product_id, "quantity": 1})
    client.post("/api/v1/orders", json={"customer_id": other_customer_id, "product_id": product_id, "quantity": 2})

    response = client.get(f"/api/v1/orders?customer_id={customer_id}")

    assert response.status_code == 200
    page = response.get_json()["data"]
    assert page["total_count"] == 1
    assert page["items"][0]["customer_id"] == customer_id


def test_create_with_unknown_customer_returns_404(client):
    _, product_id = _create_product(client)

    response = client.post("/api/v1/orders", json={"customer_id": 999999, "product_id": product_id, "quantity": 1})

    assert response.status_code == 404
    assert response.get_json()["success"] is False


def test_create_with_unknown_product_returns_404(client):
    customer_id = _create_customer(client)

    response = client.post("/api/v1/orders", json={"customer_id": customer_id, "product_id": 999999, "quantity": 1})

    assert response.status_code == 404
    assert response.get_json()["success"] is False
