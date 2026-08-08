from apiflask import Schema
from apiflask.fields import Boolean, Email, Integer, String
from apiflask.validators import Length


class RegisterSchema(Schema):
    first_name = String(required=True, validate=Length(min=1, max=50))
    last_name = String(required=True, validate=Length(min=1, max=100))
    email = Email(required=True, validate=Length(max=100))
    password = String(required=True, validate=Length(min=8), load_only=True)


class UserSchema(Schema):
    id = Integer(dump_only=True)
    first_name = String(dump_only=True)
    last_name = String(dump_only=True)
    email = Email(dump_only=True)
    enabled = Boolean(dump_only=True)


class LoginSchema(Schema):
    email = Email(required=True)
    password = String(required=True, load_only=True)


class TokenSchema(Schema):
    access_token = String(dump_only=True)


class ConfirmEmailSchema(Schema):
    email = Email(required=True)
    token = String(required=True)


class ResendConfirmationSchema(Schema):
    email = Email(required=True)


class ForgotPasswordSchema(Schema):
    email = Email(required=True)


class ResetPasswordSchema(Schema):
    email = Email(required=True)
    token = String(required=True)
    new_password = String(required=True, validate=Length(min=8), load_only=True)
