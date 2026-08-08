from flask import jsonify
from flask_jwt_extended import jwt_required

from flask_tutorial.auth_decorators import require_permission
from flask_tutorial.schemas.common import ApiResponse
from flask_tutorial.schemas.customer import (
    CustomerPageOut,
    CustomerQuerySchema,
    CustomerSchema,
)
from flask_tutorial.services.customer_service import CustomerService

from . import customers_bp

service = CustomerService()


@customers_bp.get("")
@customers_bp.doc(security="BearerAuth")
@jwt_required()
@customers_bp.input(CustomerQuerySchema, location="query")
@customers_bp.output(CustomerPageOut)
def get_customers(query_data):
    page_response = service.get_all(query_data["page"], query_data["page_size"], search=query_data["search"])
    return ApiResponse.ok(page_response, "Customers retrieved")


@customers_bp.post("")
@customers_bp.doc(security="BearerAuth")
@require_permission("customers", "create")
@customers_bp.input(CustomerSchema)
@customers_bp.output(CustomerSchema, status_code=201)
def create_customer(json_data):
    customer = service.create(
        json_data["first_name"],
        json_data["last_name"],
        json_data["telephone"],
        json_data["email"],
        json_data["address"],
    )
    return ApiResponse.ok(customer, "Customer created")


@customers_bp.get("/<int:customer_id>")
@customers_bp.doc(security="BearerAuth")
@jwt_required()
@customers_bp.output(CustomerSchema)
def get_customer(customer_id):
    customer = service.get_by_id(customer_id)
    return ApiResponse.ok(customer, "Customer retrieved")


@customers_bp.put("/<int:customer_id>")
@customers_bp.doc(security="BearerAuth")
@require_permission("customers", "update")
@customers_bp.input(CustomerSchema)
@customers_bp.output(CustomerSchema)
def update_customer(customer_id, json_data):
    customer = service.update(
        customer_id,
        json_data["first_name"],
        json_data["last_name"],
        json_data["telephone"],
        json_data["email"],
        json_data["address"],
    )
    return ApiResponse.ok(customer, "Customer updated")


@customers_bp.delete("/<int:customer_id>")
@customers_bp.doc(security="BearerAuth")
@require_permission("customers", "delete")
def delete_customer(customer_id):
    service.delete(customer_id)
    return jsonify(ApiResponse.ok(None, "Customer deleted").to_dict()), 200
