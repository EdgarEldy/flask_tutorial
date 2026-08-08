from apiflask import Schema
from apiflask.fields import Integer, String
from apiflask.validators import Length, Range

from flask_tutorial.schemas.common import make_page_schema


class CategorySchema(Schema):
    id = Integer(dump_only=True)
    category_name = String(required=True, validate=Length(min=1, max=255))


class CategoryQuerySchema(Schema):
    page = Integer(load_default=1, validate=Range(min=1))
    page_size = Integer(load_default=20, validate=Range(min=1, max=100))


CategoryPageOut = make_page_schema(CategorySchema, "CategoryPageOut")
