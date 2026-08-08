from apiflask import APIFlask

from flask_tutorial.config import config_by_name
from flask_tutorial.error_handlers import register_error_handlers
from flask_tutorial.extensions import db, jwt, mail, migrate
from flask_tutorial.schemas.common import ApiResponseSchema


def create_app(config_name: str = "development") -> APIFlask:
    app = APIFlask(__name__, title="flask_tutorial API", version="1.0.0")
    app.config.from_object(config_by_name[config_name])

    # Registers the Bearer JWT scheme so Swagger UI shows an "Authorize" button;
    # actual protected endpoints start requiring it in feature/auth.
    app.security_schemes = {
        "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"},
    }

    # Every @app.output(SomeSchema)-decorated view gets wrapped in the
    # ApiResponse envelope automatically, with SomeSchema documented under
    # "data" in the OpenAPI spec (see ApiResponseSchema's docstring).
    app.config["BASE_RESPONSE_SCHEMA"] = ApiResponseSchema
    app.config["BASE_RESPONSE_DATA_KEY"] = "data"

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)

    register_error_handlers(app)

    from flask_tutorial.blueprints.health.views import health_bp

    app.register_blueprint(health_bp)

    return app
