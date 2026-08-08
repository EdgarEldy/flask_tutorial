import pytest

from flask_tutorial.extensions import db
from flask_tutorial.models.category import Category


@pytest.fixture(autouse=True)
def clean_categories_table(app):
    with app.app_context():
        db.session.query(Category).delete()
        db.session.commit()
    yield
    with app.app_context():
        db.session.query(Category).delete()
        db.session.commit()
