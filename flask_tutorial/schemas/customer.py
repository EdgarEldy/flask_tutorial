from apiflask import Schema
from apiflask.fields import Email, Integer, String
from apiflask.validators import Length, Range

from flask_tutorial.schemas.common import make_page_schema


class CustomerSchema(Schema):
    id = Integer(dump_only=True)
    first_name = String(required=True, validate=Length(min=1, max=255))
    last_name = String(required=True, validate=Length(min=1, max=255))
    telephone = String(required=True, validate=Length(min=1, max=50))
    email = Email(required=True, validate=Length(max=255))
    address = String(required=True, validate=Length(min=1, max=255))


class CustomerQuerySchema(Schema):
    page = Integer(load_default=1, validate=Range(min=1))
    page_size = Integer(load_default=20, validate=Range(min=1, max=100))
    search = String(load_default=None)


CustomerPageOut = make_page_schema(CustomerSchema, "CustomerPageOut")
