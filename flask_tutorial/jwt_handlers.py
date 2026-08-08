from flask import jsonify

from flask_tutorial.extensions import db, jwt
from flask_tutorial.models.identity.blacklisted_token import BlacklistedToken
from flask_tutorial.schemas.common import ApiResponse


def register_jwt_handlers(app):
    @jwt.token_in_blocklist_loader
    def check_if_token_is_blacklisted(_jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        return db.session.query(BlacklistedToken.query.filter_by(jti=jti).exists()).scalar()

    @jwt.unauthorized_loader
    def handle_missing_token(_reason):
        return jsonify(ApiResponse.fail("Missing or invalid authentication token").to_dict()), 401

    @jwt.invalid_token_loader
    def handle_invalid_token(_reason):
        return jsonify(ApiResponse.fail("Invalid authentication token").to_dict()), 401

    @jwt.expired_token_loader
    def handle_expired_token(_jwt_header, _jwt_payload):
        return jsonify(ApiResponse.fail("Token has expired").to_dict()), 401

    @jwt.revoked_token_loader
    def handle_revoked_token(_jwt_header, _jwt_payload):
        return jsonify(ApiResponse.fail("Token has been revoked").to_dict()), 401
