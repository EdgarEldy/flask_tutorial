from apiflask import APIBlueprint

orders_bp = APIBlueprint("orders", __name__, url_prefix="/api/v1/orders", tag="Orders")
