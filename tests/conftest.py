import pytest

from flask_tutorial import create_app


@pytest.fixture
def app():
    app = create_app("testing")
    yield app


@pytest.fixture
def client(app):
    return app.test_client()
