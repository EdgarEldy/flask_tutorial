"""
Routes and views for the flask application.
"""

from flask import render_template
from flask_tutorial import app

@app.route('/')
def home_index():
    """Renders the home page."""
    return render_template(
        'home/index.html'
    )


