from flask import Flask
from flask_sqlalchemy import SQLAlchemy  


app = Flask(__name__)

app.secret_key = "hello"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./data.db"

db = SQLAlchemy(app)

from routes import *


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)    