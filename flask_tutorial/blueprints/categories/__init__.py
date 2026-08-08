from apiflask import APIBlueprint

categories_bp = APIBlueprint("categories", __name__, url_prefix="/api/v1/categories", tag="Categories")
