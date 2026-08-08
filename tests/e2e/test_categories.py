import pytest

from flask_tutorial.extensions import db
from flask_tutorial.models.category import Category


@pytest.fixture(autouse=True)
def clean_categories_table(app):
    # Scoped to this module only (not tests/e2e/conftest.py) so sibling e2e
    # tests that don't touch the categories table (health, validation-error
    # envelope probes) don't pick up an unrelated database dependency.
    with app.app_context():
        db.session.query(Category).delete()
        db.session.commit()
    yield
    with app.app_context():
        db.session.query(Category).delete()
        db.session.commit()


def test_full_crud_lifecycle(client):
    create_response = client.post("/api/v1/categories", json={"category_name": "Books"})
    assert create_response.status_code == 201
    created = create_response.get_json()
    assert created["success"] is True
    category_id = created["data"]["id"]
    assert created["data"]["category_name"] == "Books"

    list_response = client.get("/api/v1/categories?page=1&page_size=20")
    assert list_response.status_code == 200
    page = list_response.get_json()["data"]
    assert page["total_count"] == 1
    assert page["items"][0]["id"] == category_id

    detail_response = client.get(f"/api/v1/categories/{category_id}")
    assert detail_response.status_code == 200
    assert detail_response.get_json()["data"]["category_name"] == "Books"

    update_response = client.put(f"/api/v1/categories/{category_id}", json={"category_name": "Books & Comics"})
    assert update_response.status_code == 200
    assert update_response.get_json()["data"]["category_name"] == "Books & Comics"

    delete_response = client.delete(f"/api/v1/categories/{category_id}")
    assert delete_response.status_code == 200
    assert delete_response.get_json()["success"] is True

    after_delete_response = client.get(f"/api/v1/categories/{category_id}")
    assert after_delete_response.status_code == 404


def test_get_detail_returns_404_api_response_for_unknown_id(client):
    response = client.get("/api/v1/categories/999999")

    assert response.status_code == 404
    body = response.get_json()
    assert body["success"] is False
    assert body["data"] is None


def test_create_with_missing_field_returns_400_with_field_errors(client):
    response = client.post("/api/v1/categories", json={})

    assert response.status_code == 400
    body = response.get_json()
    assert body["success"] is False
    assert "category_name" in body["errors"]["json"]


def test_list_is_paginated(client):
    for i in range(3):
        client.post("/api/v1/categories", json={"category_name": f"Category {i}"})

    response = client.get("/api/v1/categories?page=1&page_size=2")

    assert response.status_code == 200
    page = response.get_json()["data"]
    assert len(page["items"]) == 2
    assert page["total_count"] == 3
    assert page["total_pages"] == 2
