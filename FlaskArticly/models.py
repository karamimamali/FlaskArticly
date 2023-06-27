from main import db
from datetime import datetime


class Users(db.Model):
    __tablename__ = "Users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    email = db.Column(db.String(), unique=True)
    username = db.Column(db.String(), unique=True)
    password = db.Column(db.String())

class Articles(db.Model):
    __tablename__ = "Articles"

    id = db.Column("id",db.Integer, primary_key=True)
    title = db.Column("title",db.String())
    author = db.Column("author",db.String())
    content = db.Column("content",db.String())
    date = db.Column("date",db.DateTime, default=datetime.utcnow)

