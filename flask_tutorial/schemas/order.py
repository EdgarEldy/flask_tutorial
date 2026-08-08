from apiflask import Schema
from apiflask.fields import Float, Integer
from apiflask.validators import Range

from flask_tutorial.schemas.common import make_page_schema


class OrderSchema(Schema):
    id = Integer(dump_only=True)
    customer_id = Integer(required=True)
    product_id = Integer(required=True)
    quantity = Integer(required=True, validate=Range(min=1))
    total = Float(dump_only=True)


class OrderQuerySchema(Schema):
    page = Integer(load_default=1, validate=Range(min=1))
    page_size = Integer(load_default=20, validate=Range(min=1, max=100))
    customer_id = Integer(load_default=None)
    product_id = Integer(load_default=None)


OrderPageOut = make_page_schema(OrderSchema, "OrderPageOut")
