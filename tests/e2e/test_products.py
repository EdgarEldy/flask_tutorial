import pytest

from flask_tutorial.extensions import db
from flask_tutorial.models.category import Category
from flask_tutorial.models.product import Product


@pytest.fixture(autouse=True)
def clean_tables(app):
    with app.app_context():
        db.session.query(Product).delete()
        db.session.query(Category).delete()
        db.session.commit()
    yield
    with app.app_context():
        db.session.query(Product).delete()
        db.session.query(Category).delete()
        db.session.commit()


def _create_category(client, name="Electronics") -> int:
    response = client.post("/api/v1/categories", json={"category_name": name})
    return response.get_json()["data"]["id"]


def test_full_crud_lifecycle(client):
    category_id = _create_category(client)

    create_response = client.post(
        "/api/v1/products", json={"category_id": category_id, "product_name": "Laptop", "unit_price": 999.99}
    )
    assert create_response.status_code == 201
    created = create_response.get_json()["data"]
    product_id = created["id"]
    assert created["product_name"] == "Laptop"

    detail_response = client.get(f"/api/v1/products/{product_id}")
    assert detail_response.status_code == 200
    assert detail_response.get_json()["data"]["unit_price"] == 999.99

    update_response = client.put(
        f"/api/v1/products/{product_id}",
        json={"category_id": category_id, "product_name": "Laptop Pro", "unit_price": 1299.99},
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["data"]["product_name"] == "Laptop Pro"

    delete_response = client.delete(f"/api/v1/products/{product_id}")
    assert delete_response.status_code == 200

    after_delete_response = client.get(f"/api/v1/products/{product_id}")
    assert after_delete_response.status_code == 404


def test_category_id_filter_on_the_products_list(client):
    electronics_id = _create_category(client, "Electronics")
    books_id = _create_category(client, "Books")

    client.post("/api/v1/products", json={"category_id": electronics_id, "product_name": "Laptop", "unit_price": 999.99})
    client.post("/api/v1/products", json={"category_id": books_id, "product_name": "Novel", "unit_price": 9.99})

    response = client.get(f"/api/v1/products?category_id={electronics_id}")

    assert response.status_code == 200
    page = response.get_json()["data"]
    assert page["total_count"] == 1
    assert page["items"][0]["product_name"] == "Laptop"


def test_get_detail_returns_404_api_response_for_unknown_id(client):
    response = client.get("/api/v1/products/999999")

    assert response.status_code == 404
    assert response.get_json()["success"] is False


def test_delete_category_with_products_returns_422(client):
    category_id = _create_category(client)
    client.post("/api/v1/products", json={"category_id": category_id, "product_name": "Laptop", "unit_price": 999.99})

    response = client.delete(f"/api/v1/categories/{category_id}")

    assert response.status_code == 422
    body = response.get_json()
    assert body["success"] is False
