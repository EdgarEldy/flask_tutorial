from apiflask import APIBlueprint

products_bp = APIBlueprint("products", __name__, url_prefix="/api/v1/products", tag="Products")
