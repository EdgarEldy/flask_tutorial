from flask import Blueprint, jsonify

from flask_tutorial.schemas.common import ApiResponse
from flask_tutorial.services.health_service import HealthService

health_bp = Blueprint("health", __name__, url_prefix="/health")


@health_bp.get("")
def get_health():
    status = HealthService().get_status()
    return jsonify(ApiResponse.ok(status, "Service is healthy").to_dict()), 200
