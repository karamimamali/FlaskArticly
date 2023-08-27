from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.secret_key = "snoc6483mc02b\d/b.s,v229^$^%f0v(**V63ov)"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./data.db"
db = SQLAlchemy(app=app)



from .routes import *