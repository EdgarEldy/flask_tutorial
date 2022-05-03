from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Setting up database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask_db'
db = SQLAlchemy(app)

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
