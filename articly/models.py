from articly.__init__ import db
from datetime import datetime



class User(db.Model):
    __tablename__ = "user"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    articles = db.relationship("Article",backref = "user" , passive_deletes = True)
    likes = db.relationship("Like",backref = "user" , passive_deletes = True)
    comments = db.relationship("Comment",backref = "user" , passive_deletes = True)



class Article(db.Model):
    __tablename__ = "article"
    __table_args__ = {'extend_existing': True}

    id = db.Column("id",db.Integer, primary_key=True)
    title = db.Column("title",db.String(150))
    author = db.Column(db.String, db.ForeignKey("user.id",ondelete= "CASCADE"),nullable = False)
    content = db.Column("content",db.String())
    date = db.Column("date",db.DateTime, default=datetime.utcnow)
    likes = db.relationship("Like",backref = "article" , passive_deletes = True)
    comments = db.relationship("Comment",backref = "article" , passive_deletes = True)
    


class Comment(db.Model):
    __tablename__ = "comment"
    __table_args__ = {'extend_existing': True}

    id = db.Column("id",db.Integer, primary_key=True)
    author = db.Column(db.String, db.ForeignKey("user.id",ondelete= "CASCADE"),nullable = False)
    content = db.Column("content",db.String())
    date = db.Column("date",db.DateTime, default=datetime.utcnow)
    article_id = db.Column(db.Integer, db.ForeignKey("article.id",ondelete= "CASCADE"),nullable = False)
    
    

class Like(db.Model):
    __tablename__ = "like"
    __table_args__ = {'extend_existing': True}

    id = db.Column("id",db.Integer, primary_key=True)
    author = db.Column(db.Integer, db.ForeignKey("user.id",ondelete= "CASCADE"),nullable = False)
    article_id = db.Column(db.Integer, db.ForeignKey("article.id",ondelete= "CASCADE"),nullable = False)
    