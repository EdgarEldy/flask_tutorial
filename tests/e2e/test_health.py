def test_health_returns_200(client):
    response = client.get("/health")

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["status"] == "up"
    assert body["data"]["database"] in {"up", "down"}


def test_unmatched_route_returns_404_api_response(client):
    response = client.get("/this-route-does-not-exist")

    assert response.status_code == 404
    body = response.get_json()
    assert body["success"] is False
    assert body["message"] == "Resource not found"
    assert body["data"] is None
