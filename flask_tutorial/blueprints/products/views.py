from flask import jsonify
from flask.views import MethodView

from flask_tutorial.schemas.common import ApiResponse
from flask_tutorial.schemas.product import (
    ProductPageOut,
    ProductQuerySchema,
    ProductSchema,
)
from flask_tutorial.services.product_service import ProductService

from . import products_bp


class ProductListView(MethodView):
    def __init__(self):
        self.service = ProductService()

    @products_bp.input(ProductQuerySchema, location="query")
    @products_bp.output(ProductPageOut)
    def get(self, query_data):
        page_response = self.service.get_all(
            query_data["page"], query_data["page_size"], category_id=query_data["category_id"]
        )
        return ApiResponse.ok(page_response, "Products retrieved")

    @products_bp.input(ProductSchema)
    @products_bp.output(ProductSchema, status_code=201)
    def post(self, json_data):
        product = self.service.create(
            json_data["category_id"], json_data["product_name"], json_data["unit_price"]
        )
        return ApiResponse.ok(product, "Product created")


class ProductDetailView(MethodView):
    def __init__(self):
        self.service = ProductService()

    @products_bp.output(ProductSchema)
    def get(self, product_id):
        product = self.service.get_by_id(product_id)
        return ApiResponse.ok(product, "Product retrieved")

    @products_bp.input(ProductSchema)
    @products_bp.output(ProductSchema)
    def put(self, product_id, json_data):
        product = self.service.update(
            product_id, json_data["category_id"], json_data["product_name"], json_data["unit_price"]
        )
        return ApiResponse.ok(product, "Product updated")

    def delete(self, product_id):
        self.service.delete(product_id)
        return jsonify(ApiResponse.ok(None, "Product deleted").to_dict()), 200


product_list_view = ProductListView.as_view("product_list")
products_bp.add_url_rule("", view_func=product_list_view, methods=["GET", "POST"])

product_detail_view = ProductDetailView.as_view("product_detail")
products_bp.add_url_rule(
    "/<int:product_id>", view_func=product_detail_view, methods=["GET", "PUT", "DELETE"]
)
