from apiflask import APIBlueprint

auth_bp = APIBlueprint("auth", __name__, url_prefix="/api/v1/auth", tag="Auth")
