from apiflask import Schema
from apiflask.fields import Float, Integer, String
from apiflask.validators import Length, Range

from flask_tutorial.schemas.common import make_page_schema


class ProductSchema(Schema):
    id = Integer(dump_only=True)
    category_id = Integer(required=True)
    product_name = String(required=True, validate=Length(min=1, max=255))
    unit_price = Float(required=True, validate=Range(min=0, min_inclusive=False))


class ProductQuerySchema(Schema):
    page = Integer(load_default=1, validate=Range(min=1))
    page_size = Integer(load_default=20, validate=Range(min=1, max=100))
    category_id = Integer(load_default=None)


ProductPageOut = make_page_schema(ProductSchema, "ProductPageOut")
