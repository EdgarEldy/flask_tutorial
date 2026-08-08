import logging

from flask import jsonify
from marshmallow import ValidationError

from flask_tutorial.errors import BusinessRuleError, ResourceNotFoundError
from flask_tutorial.schemas.common import ApiResponse

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    # APIFlask's own validation errors (raised internally by @app.input()) and
    # any HTTPError/abort()/Werkzeug HTTP exception never reach a plain
    # @app.errorhandler(marshmallow.ValidationError) - APIFlask catches the raw
    # marshmallow error itself and re-raises its own HTTPError subclass, handled
    # by this app-wide processor instead. See apiflask.APIFlask.error_processor.
    app.config["VALIDATION_ERROR_STATUS_CODE"] = 400

    @app.error_processor
    def handle_api_flask_error(error):
        response = ApiResponse.fail(error.message or "Request failed")
        payload = response.to_dict()
        if error.detail:
            payload["errors"] = error.detail
        return payload, error.status_code, error.headers

    @app.errorhandler(ResourceNotFoundError)
    def handle_not_found(err: ResourceNotFoundError):
        return jsonify(ApiResponse.fail(err.message).to_dict()), 404

    @app.errorhandler(ValidationError)
    def handle_validation_error(err: ValidationError):
        # For marshmallow.ValidationError raised manually (e.g. schema.load()
        # called directly in a service, outside of @app.input()).
        response = ApiResponse.fail("Validation failed")
        payload = response.to_dict()
        payload["errors"] = err.messages
        return jsonify(payload), 400

    @app.errorhandler(BusinessRuleError)
    def handle_business_rule(err: BusinessRuleError):
        return jsonify(ApiResponse.fail(err.message).to_dict()), 422

    @app.errorhandler(404)
    def handle_not_found_route(_err):
        return jsonify(ApiResponse.fail("Resource not found").to_dict()), 404

    @app.errorhandler(Exception)
    def handle_unexpected_error(err: Exception):
        logger.exception("Unhandled exception")
        return jsonify(ApiResponse.fail("An unexpected error occurred").to_dict()), 500
