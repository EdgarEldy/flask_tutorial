from apiflask import APIBlueprint

customers_bp = APIBlueprint("customers", __name__, url_prefix="/api/v1/customers", tag="Customers")
