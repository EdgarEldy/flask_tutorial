"""Guards against APIFlask intercepting @app.input() validation failures
before they reach our ApiResponse envelope (see app.error_processor in
error_handlers.py) - a plain @app.errorhandler(marshmallow.ValidationError)
alone does not catch these, since APIFlask re-raises its own HTTPError
subclass internally.
"""

from apiflask import Schema
from apiflask.fields import String


class _ProbeSchema(Schema):
    name = String(required=True)


def test_app_input_validation_failure_uses_api_response_envelope(app):
    @app.post("/__test_probe")
    @app.input(_ProbeSchema)
    def probe(json_data):
        return {"ok": True}

    client = app.test_client()
    response = client.post("/__test_probe", json={})

    assert response.status_code == 400
    body = response.get_json()
    assert body["success"] is False
    assert body["errors"] == {"json": {"name": ["Missing data for required field."]}}
