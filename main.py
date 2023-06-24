from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import func
from datetime import datetime





# app and database configurations
app = Flask(__name__)
app.secret_key = "hello"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./data.db"
db = SQLAlchemy(app)

#----------------------------------------------------------------------------------------
# Tables



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


#----------------------------------------------------------------------------------------
# Decorator


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("you need to log in in order to see dashboard page",'danger')
            return redirect(url_for('daxil_ol'))
    return decorated_function


#----------------------------------------------------------------------------------------
# Forms


class RegisterForm(Form):
    name = StringField("name",render_kw={'style': 'width: 20ch' } ,validators=[validators.length(min=1,max=25)])
    username = StringField("username",render_kw={'style': 'width: 20ch'}, validators=[validators.length(min=1,max= 25)])
    email = StringField("email",render_kw={'style': 'width: 20ch'})
    password = PasswordField("password",render_kw={'style': 'width: 20ch'},validators=[
        validators.DataRequired(message="Enter a password"),
        validators.EqualTo(fieldname="confirm", message="passwords doesn't match")
    ])
    confirm = PasswordField("confirm your password",render_kw={'style': 'width: 20ch'})

class LogInForm(Form):
    username = StringField('username')
    password = PasswordField('password')

class ArticleForm(Form):
    title = StringField('title',validators=[validators.length(min=5,max=100)])
    content = TextAreaField('content',validators=[validators.length(min=10)])


#----------------------------------------------------------------------------------------
#functions


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/dashboard')
@login_required
def dashboard():
    try:
        result = db.session.execute(db.select(Articles).filter_by(author=session["username"]))              
        return render_template('dashboard.html',articles=result)
    except:
        return render_template('dashboard.html')


@app.route('/articles')
def articles():
    try:
        result = db.session.execute(db.select(Articles))
        return render_template('articles.html',articles=result)   
    except:
        return render_template('articles.html')

#----------------------------------------------------------------------------------------
# Log out , log in , register

@app.route('/logout')
def cix():
    session.clear()
    return redirect(url_for('home'))

@app.route('/login', methods= ['GET','POST'])
def daxil_ol():
    form = LogInForm(request.form)
    if request.method == 'POST':
        entered_username = form.username.data
        entered_password = form.password.data

        try:
            user =db.session.execute(db.select(Users).filter_by(username=entered_username)).scalar_one()
                  
            real_password = user.password 
            if sha256_crypt.verify(entered_password,real_password):
                flash('loged in','success')
                session['logged_in'] = True
                session['username'] = entered_username
                return redirect(url_for('home'))
            else:
                flash('password is wrong','danger')
                return redirect(url_for('daxil_ol'))
           
        except:
            flash('username not found','danger')
            return redirect(url_for('daxil_ol'))

    else:
        return render_template('login.html',form=form)
    

@app.route('/register', methods = ['GET','POST'])
def register():
    form = RegisterForm(request.form)

    if request.method == 'POST' and form.validate():
        name  = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.hash(form.password.data)

        try:
            user = Users(name=name,username=username,email=email,password=password)

            db.session.add(user)
            db.session.commit()
            flash('sign up succesfully','success')
            return redirect(url_for('daxil_ol'))
        except:
            flash('username is not available','danger')
            return redirect(url_for('register'))
    else:
        return render_template('register.html',form=form)






#----------------------------------------------------------------------------------------
#detail ,add article , delet article ,update article ,search article
@app.route('/article/<id>')
def detail(id):
    try:
        result = db.session.execute(db.select(Articles).filter_by(id=id)).scalar_one()       
        return render_template('article.html',article=result)
    except:
        return render_template("article.html")
    


@app.route('/addarticle', methods=['GET','POST'])
def addarticle():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate(): 
        
        article = Articles(title=form.title.data,content=form.content.data,author=session["username"])
        db.session.add(article)
        db.session.commit()
        flash('Article added succesfully','success')
        return redirect(url_for('dashboard'))
    else:
        return render_template('addarticle.html',form = form)


@app.route('/delete/<string:id>')
@login_required
def delete(id):
    try:
        article = db.session.execute(db.select(Articles).filter_by(id=id,author=session["username"])).scalar_one()       
        db.session.delete(article)
        db.session.commit()

        flash('article deleted','warning')
        return redirect(url_for('dashboard'))
    except:
        flash("there is no such article or you do not have permission to delete this article",'danger')
        return redirect(url_for('home'))

@app.route('/edit/<string:id>', methods=['GET','POST'])
@login_required
def update(id):
    if request.method == 'GET':              
        try:
            article = db.session.execute(db.select(Articles).filter_by(id=id,author=session["username"])).scalar_one()
            
            form = ArticleForm()

            form.title.data = article.title
            form.content.data = article.content
            return render_template('edit.html',form=form)
        
        except:
            flash('there is no such an article or you do not have permmisson','danger')
            return redirect(url_for('home'))
            
    else:
        form = ArticleForm(request.form)

        new_title = form.title.data
        new_content = form.content.data

        article = db.session.execute(db.select(Articles).filter_by(id=id)).scalar_one_or_none()

        article.title = new_title
        article.content = new_content
        db.session.commit()

        flash('Article updated','success')
        return redirect(url_for('dashboard'))


@app.route('/search', methods= ['GET','POST'])
def search():
    if request.method == 'GET':
        return redirect(url_for('home'))
    else:    
        keyword = request.form.get("keyword")
        search = "%{}%".format(keyword)         
        articles = Articles.query.filter(Articles.title.like(search))
        if articles:
            return render_template('search.html',articles = articles)
        
        return render_template('articles.html')
                


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)    