"""Guards the BASE_RESPONSE_SCHEMA wiring (ApiResponseSchema, set in
create_app()): a view using @app.output(SomeSchema) must come back as
the same ApiResponse envelope shape - and the same ISO-8601 timestamp
format - as the manual jsonify(ApiResponse.ok(...).to_dict()) path used
by error_handlers.py and /health.
"""

import re

from apiflask import Schema
from apiflask.fields import Integer, String

from flask_tutorial.schemas.common import ApiResponse

ISO_8601 = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(\+00:00|Z)$")


class _ProbeOutSchema(Schema):
    id = Integer()
    label = String()


def test_app_output_uses_the_same_envelope_and_timestamp_format(app):
    @app.get("/__test_probe_output")
    @app.output(_ProbeOutSchema)
    def probe():
        return ApiResponse.ok({"id": 1, "label": "widget"}, "Probe retrieved")

    client = app.test_client()
    response = client.get("/__test_probe_output")

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["message"] == "Probe retrieved"
    assert body["data"] == {"id": 1, "label": "widget"}
    assert ISO_8601.match(body["timestamp"]), body["timestamp"]
