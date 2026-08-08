"""
This script runs the flask_tutorial application using a development server.
"""

import os

from flask_tutorial import create_app

app = create_app(os.environ.get("FLASK_ENV", "development"))

if __name__ == "__main__":
    HOST = os.environ.get("SERVER_HOST", "localhost")
    try:
        PORT = int(os.environ.get("SERVER_PORT", "5000"))
    except ValueError:
        PORT = 5000
    app.run(HOST, PORT)
