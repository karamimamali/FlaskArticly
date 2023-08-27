from flask import render_template, flash, redirect, url_for, session, request, Blueprint
from passlib.hash import sha256_crypt
from functools import wraps
from articly.forms import RegisterForm, LogInForm ,ArticleForm ,CommentForm
from articly.__init__ import db ,app
from articly.models import Article, User, Like, Comment
from sqlalchemy import func 


bp = Blueprint('bp', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to log in first",'danger')
            return redirect(url_for('LoginUser'))
    return decorated_function



@app.route('/')
def home():
    top_articles = db.session.query(Article).join(Like).group_by(Article).order_by(func.count(Like.id).desc()).limit(6).all()  
    return render_template('blog/index.html',articles=top_articles)



@app.route('/about')
def about():
    return render_template('blog/about.html')


@app.route('/dashboard')
@login_required
def dashboard():
    session.pop('page',None)
    session['page'] = 'dashboard'
    
    user = db.session.execute(db.select(User).filter_by(username=session['username'])).scalar()
    articles = db.session.query(Article).filter_by(author=user.id).all()      
    return render_template('blog/dashboard.html',articles=articles,user=user)


@app.route('/articles')
def articles():
    session.pop('page',None)
    session['page'] = 'articles'

    articles = db.session.query(Article).all()
    try:
        user = db.session.execute(db.select(User).filter_by(username=session['username'])).scalar()
    except:
        user = None
    return render_template('blog/articles.html',articles=articles,user = user)   
    

@app.route('/logout')
def LogoutUser():
    session.clear()
    return redirect(url_for('home'))



@app.route('/login', methods= ['GET','POST'])
def LoginUser():
    form = LogInForm(request.form)

    if request.method == 'GET':
        return render_template('auth/login.html',form=form)
    
    entered_username = form.username.data
    entered_password = form.password.data
    user = db.session.execute(db.select(User).filter_by(username=entered_username)).scalar()

    if not user:
        flash('username not found','danger')
        return redirect(url_for('LoginUser'))
    
    real_password = user.password 

    if not sha256_crypt.verify(entered_password,real_password):
        flash('password is wrong','danger')
        return redirect(url_for('LoginUser'))

    flash('logged in','success')
    session['username'] = entered_username
    session['logged_in'] = True
    return redirect(url_for('home'))
            


def email_already_exist(email) -> bool:
    exist = db.session.execute(db.select(User).filter_by(email=email)).scalar()
    if exist:
        return True
    return False

def username_already_exist(username) -> bool:
    exist = db.session.execute(db.select(User).filter_by(username=username)).scalar()
    if exist:
        return True
    return False


@app.route('/register', methods = ['GET','POST'])
def RegisterUser():
    form = RegisterForm(request.form)

    if request.method == 'GET' or not form.validate(): 
        return render_template('auth/register.html',form=form)
    
    name  = form.name.data
    username = form.username.data
    email = form.email.data
    password = sha256_crypt.hash(form.password.data)

    if username_already_exist(username):
        flash('Username already exist','danger')
        return render_template('auth/register.html',form=form)
    
    if email_already_exist(email):
        flash('Email already exist','danger')
        return render_template('auth/register.html',form=form)

    user = User(name=name,email=email,username=username,password=password)
    
    db.session.add(user)
    db.session.commit()
    flash('sign up succesfully','success')
    return redirect(url_for('LoginUser'))
    


@app.route('/article/<id>')
def detail(id):
    session.pop('page',None)
    session['page'] = 'article'
    form = CommentForm(request.form)

    try:
        user = db.session.execute(db.select(User).filter_by(username=session['username'])).scalar()
    except:
        user = None
    article = db.session.execute(db.select(Article).filter_by(id=id)).scalar_one()
    return render_template("blog/article.html",article=article,form=form,user=user)
   

@app.route('/addarticle', methods=['GET','POST'])
@login_required
def addarticle():
    form = ArticleForm(request.form)

    if request.method == 'GET' or not form.validate():
        return render_template('blog/addarticle.html',form = form) 
    
    user = db.session.execute(db.select(User).filter_by(username=session['username'])).scalar()
    article = Article(title=form.title.data,content=form.content.data,author=user.id)
    db.session.add(article)
    db.session.commit()
    flash('Article added succesfully','success')
    return redirect(url_for('dashboard'))


@app.route('/delete/<string:id>')
@login_required
def delete(id):

    user = db.session.execute(db.select(User).filter_by(username=session['username'])).scalar()
    article = db.session.execute(db.select(Article).filter_by(id=id,author=user.id)).scalar()
    if not article:
            flash('There is no such an article','danger')
            return redirect(url_for('home'))
    
    db.session.delete(article)
    db.session.commit()
    flash('article deleted','warning')
    return redirect(url_for('dashboard'))


@app.route('/edit/<string:id>', methods=['GET','POST'])
@login_required
def update(id):
    if request.method == 'GET': 
        user = db.session.execute(db.select(User).filter_by(username=session['username'])).scalar()
        article = db.session.execute(db.select(Article).filter_by(id=id,author=user.id)).scalar()
        if not article:
            flash('there is no such an article or you do not have permmisson','danger')
            return redirect(url_for('home'))
        
        form = ArticleForm()

        form.title.data = article.title
        form.content.data = article.content
        return render_template('blog/edit.html',form=form)
    
    
    form = ArticleForm(request.form)

    new_title = form.title.data
    new_content = form.content.data
    
    article = db.session.execute(db.select(Article).filter_by(id=id)).scalar()

    article.title = new_title
    article.content = new_content
    db.session.commit()
    flash('Article updated','success')
    return redirect(url_for('dashboard'))


@app.route('/search', methods= ['POST'])
def search():
    keyword = request.form.get("keyword")
    articles = Article.query.filter(Article.title.like(f"%{keyword}%"))
    try:
        user = db.session.execute(db.select(User).filter_by(username=session['username'])).scalar()
    except:
        user = None
    return render_template('blog/articles.html',articles = articles,user=user)
                

@app.route('/like/<string:article_id>')
@login_required
def like(article_id):
    article = db.session.execute(db.select(Article).filter_by(id = article_id)).scalar()
    user = db.session.execute(db.select(User).filter_by(username = session['username'])).scalar()
    like = db.session.execute(db.select(Like).filter_by(author = user.id,article_id=article.id)).scalar()

    if not article:
        flash("There is no article like that",'danger')
        return redirect(url_for('home'))
    
    if like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(author = user.id, article_id = article.id)
        db.session.add(like)
        db.session.commit()


    if session['page'] == 'articles':
        return redirect(url_for('articles'))
    
    elif session['page'] == 'dashboard':
        return redirect(url_for('dashboard'))
        
    else:
        return redirect(url_for('detail',id=article_id))


@app.route('/addcomment/<article_id>',methods=['POST','GET'])
@login_required
def addcomment(article_id):
    form = CommentForm(request.form)
    if request.method == 'GET' or not form.validate():
        return render_template('blog/addcomment.html',form = form)
    
    user = db.session.execute(db.select(User).filter_by(username=session['username'])).scalar()
    comment = Comment(content=form.content.data, author=user.id, article_id=article_id)
    db.session.add(comment)
    db.session.commit()
    flash('Comment added succesfully','success')
    return redirect(url_for('blog/detail',id=article_id))
