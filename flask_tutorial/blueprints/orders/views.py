from flask import jsonify
from flask.views import MethodView

from flask_tutorial.schemas.common import ApiResponse
from flask_tutorial.schemas.order import OrderPageOut, OrderQuerySchema, OrderSchema
from flask_tutorial.services.order_service import OrderService

from . import orders_bp


class OrderListView(MethodView):
    def __init__(self):
        self.service = OrderService()

    @orders_bp.input(OrderQuerySchema, location="query")
    @orders_bp.output(OrderPageOut)
    def get(self, query_data):
        page_response = self.service.get_all(
            query_data["page"],
            query_data["page_size"],
            customer_id=query_data["customer_id"],
            product_id=query_data["product_id"],
        )
        return ApiResponse.ok(page_response, "Orders retrieved")

    @orders_bp.input(OrderSchema)
    @orders_bp.output(OrderSchema, status_code=201)
    def post(self, json_data):
        order = self.service.create(
            json_data["customer_id"], json_data["product_id"], json_data["quantity"]
        )
        return ApiResponse.ok(order, "Order created")


class OrderDetailView(MethodView):
    def __init__(self):
        self.service = OrderService()

    @orders_bp.output(OrderSchema)
    def get(self, order_id):
        order = self.service.get_by_id(order_id)
        return ApiResponse.ok(order, "Order retrieved")

    @orders_bp.input(OrderSchema)
    @orders_bp.output(OrderSchema)
    def put(self, order_id, json_data):
        order = self.service.update(
            order_id, json_data["customer_id"], json_data["product_id"], json_data["quantity"]
        )
        return ApiResponse.ok(order, "Order updated")

    def delete(self, order_id):
        self.service.delete(order_id)
        return jsonify(ApiResponse.ok(None, "Order deleted").to_dict()), 200


order_list_view = OrderListView.as_view("order_list")
orders_bp.add_url_rule("", view_func=order_list_view, methods=["GET", "POST"])

order_detail_view = OrderDetailView.as_view("order_detail")
orders_bp.add_url_rule("/<int:order_id>", view_func=order_detail_view, methods=["GET", "PUT", "DELETE"])
