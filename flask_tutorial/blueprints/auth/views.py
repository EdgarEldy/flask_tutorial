from flask import jsonify, request
from flask_jwt_extended import jwt_required

from flask_tutorial.schemas.auth import (
    ConfirmEmailSchema,
    ForgotPasswordSchema,
    LoginSchema,
    RegisterSchema,
    ResendConfirmationSchema,
    ResetPasswordSchema,
    TokenSchema,
    UserSchema,
)
from flask_tutorial.schemas.common import ApiResponse
from flask_tutorial.services.auth_service import AuthService

from . import auth_bp

service = AuthService()


@auth_bp.post("/register")
@auth_bp.input(RegisterSchema)
@auth_bp.output(UserSchema, status_code=201)
def register(json_data):
    user = service.register(
        json_data["first_name"], json_data["last_name"], json_data["email"], json_data["password"]
    )
    return ApiResponse.ok(user, "Registration successful, check your email to confirm your account")


@auth_bp.post("/confirm-email")
@auth_bp.input(ConfirmEmailSchema)
def confirm_email(json_data):
    service.confirm_email(json_data["token"])
    return jsonify(ApiResponse.ok(None, "Account confirmed").to_dict()), 200


@auth_bp.post("/resend-confirmation")
@auth_bp.input(ResendConfirmationSchema)
def resend_confirmation(json_data):
    service.resend_confirmation(json_data["email"])
    return jsonify(ApiResponse.ok(None, "If that account exists, a confirmation email was sent").to_dict()), 200


@auth_bp.post("/login")
@auth_bp.input(LoginSchema)
@auth_bp.output(TokenSchema)
def login(json_data):
    access_token = service.login(json_data["email"], json_data["password"])
    return ApiResponse.ok({"access_token": access_token}, "Login successful")


@auth_bp.get("/me")
@auth_bp.doc(security="BearerAuth")
@jwt_required()
@auth_bp.output(UserSchema)
def me():
    user = service.get_current_user()
    return ApiResponse.ok(user, "Current user retrieved")


@auth_bp.post("/logout")
@auth_bp.doc(security="BearerAuth")
@jwt_required()
def logout():
    raw_token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    service.logout(raw_token)
    return jsonify(ApiResponse.ok(None, "Logged out").to_dict()), 200


@auth_bp.post("/forgot-password")
@auth_bp.input(ForgotPasswordSchema)
def forgot_password(json_data):
    service.forgot_password(json_data["email"])
    return jsonify(ApiResponse.ok(None, "If that account exists, a password reset email was sent").to_dict()), 200


@auth_bp.post("/reset-password")
@auth_bp.input(ResetPasswordSchema)
def reset_password(json_data):
    service.reset_password(json_data["token"], json_data["new_password"])
    return jsonify(ApiResponse.ok(None, "Password reset successful").to_dict()), 200
