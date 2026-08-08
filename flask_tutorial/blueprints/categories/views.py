from flask import jsonify
from flask.views import MethodView

from flask_tutorial.auth_decorators import require_permission
from flask_tutorial.schemas.category import (
    CategoryPageOut,
    CategoryQuerySchema,
    CategorySchema,
)
from flask_tutorial.schemas.common import ApiResponse
from flask_tutorial.services.category_service import CategoryService

from . import categories_bp


class CategoryListView(MethodView):
    def __init__(self):
        self.service = CategoryService()

    @categories_bp.input(CategoryQuerySchema, location="query")
    @categories_bp.output(CategoryPageOut)
    def get(self, query_data):
        page_response = self.service.get_all(query_data["page"], query_data["page_size"])
        return ApiResponse.ok(page_response, "Categories retrieved")

    @categories_bp.doc(security="BearerAuth")
    @require_permission("categories", "create")
    @categories_bp.input(CategorySchema)
    @categories_bp.output(CategorySchema, status_code=201)
    def post(self, json_data):
        category = self.service.create(json_data["category_name"])
        return ApiResponse.ok(category, "Category created")


class CategoryDetailView(MethodView):
    def __init__(self):
        self.service = CategoryService()

    @categories_bp.output(CategorySchema)
    def get(self, category_id):
        category = self.service.get_by_id(category_id)
        return ApiResponse.ok(category, "Category retrieved")

    @categories_bp.doc(security="BearerAuth")
    @require_permission("categories", "update")
    @categories_bp.input(CategorySchema)
    @categories_bp.output(CategorySchema)
    def put(self, category_id, json_data):
        category = self.service.update(category_id, json_data["category_name"])
        return ApiResponse.ok(category, "Category updated")

    @categories_bp.doc(security="BearerAuth")
    @require_permission("categories", "delete")
    def delete(self, category_id):
        self.service.delete(category_id)
        return jsonify(ApiResponse.ok(None, "Category deleted").to_dict()), 200


category_list_view = CategoryListView.as_view("category_list")
categories_bp.add_url_rule("", view_func=category_list_view, methods=["GET", "POST"])

category_detail_view = CategoryDetailView.as_view("category_detail")
categories_bp.add_url_rule(
    "/<int:category_id>", view_func=category_detail_view, methods=["GET", "PUT", "DELETE"]
)
