import pytest
from testcontainers.community.postgres import PostgresContainer

from flask_tutorial import create_app
from flask_tutorial.config import TestConfig
from flask_tutorial.extensions import db


@pytest.fixture(scope="module")
def postgres_container():
    with PostgresContainer("postgres:16", driver="psycopg") as container:
        yield container


@pytest.fixture
def app(postgres_container, monkeypatch):
    # TestConfig.SQLALCHEMY_DATABASE_URI is a class attribute set once from
    # TEST_DATABASE_URL at import time - create_app() reads it via
    # app.config.from_object(TestConfig) *before* db.init_app(app) builds the
    # engine, so overriding app.config afterwards is too late. Patch the
    # class attribute itself so create_app() picks up the ephemeral
    # container's URL from the start.
    monkeypatch.setattr(TestConfig, "SQLALCHEMY_DATABASE_URI", postgres_container.get_connection_url())
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
