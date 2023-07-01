from flask import render_template,flash, redirect, url_for, session, request
from passlib.hash import sha256_crypt
from functools import wraps
from forms import RegisterForm , LogInForm ,ArticleForm ,CommentForm
from main import app, db 
from models import Article , User , Like, Comment
from sqlalchemy import func



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("you need to log in in order to see dashboard page",'danger')
            return redirect(url_for('daxil_ol'))
    return decorated_function



@app.route('/')
def home():
    top_articles = db.session.query(Article).join(Like).group_by(Article).order_by(func.count(Like.id).desc()).limit(6).all()  
    return render_template('index.html',articles=top_articles)



@app.route('/about')
def about():
    return render_template('about.html')



@app.route('/dashboard')
@login_required
def dashboard():
    session.pop('page',None)
    session['page'] = 'dashboard'
    
    try:
        user = db.session.execute(db.select(User).filter_by(username=session['username'])).scalar()
        articles = db.session.query(Article).filter_by(author=user.id).all()      
        return render_template('dashboard.html',articles=articles,user=user)
    
    except:
        return render_template('dashboard.html')



@app.route('/articles')
def articles():
    session.pop('page',None)
    session['page'] = 'articles'

    try:
        articles = db.session.query(Article).all()
        user = db.session.execute(db.select(User).filter_by(username=session['username'])).scalar()
        return render_template('articles.html',articles=articles,user =user)   
    
    except:
        return render_template('articles.html')



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
            user =db.session.execute(db.select(User).filter_by(username=entered_username)).scalar_one()
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
            user = User(name=name,email=email,username=username,password=password)
            
            db.session.add(user)
            db.session.commit()
            flash('sign up succesfully','success')
            return redirect(url_for('daxil_ol'))
        
        except:
            flash('username is not available','danger')
            return redirect(url_for('register'))
        
    else:
        return render_template('register.html',form=form)



@app.route('/article/<id>')
def detail(id):
    session.pop('page',None)
    session['page'] = 'article'
    form = CommentForm(request.form)

    try:
        user = db.session.execute(db.select(User).filter_by(username=session['username'])).scalar()
        article = db.session.execute(db.select(Article).filter_by(id=id)).scalar_one()       
        return render_template('article.html',article=article,user=user,form=form)
    
    except:
        article = db.session.execute(db.select(Article).filter_by(id=id)).scalar_one()
        return render_template("article.html",article=article,form=form)
   


@app.route('/addarticle', methods=['GET','POST'])
def addarticle():
    form = ArticleForm(request.form)

    if request.method == 'POST' and form.validate(): 
        user = db.session.execute(db.select(User).filter_by(username=session['username'])).scalar()
        article = Article(title=form.title.data,content=form.content.data,author=user.id)
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
        user = db.session.execute(db.select(User).filter_by(username=session['username'])).scalar()
        article = db.session.execute(db.select(Article).filter_by(id=id,author=user.id)).scalar_one()       
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
            user = db.session.execute(db.select(User).filter_by(username=session['username'])).scalar()
            article = db.session.execute(db.select(Article).filter_by(id=id,author=user.id)).scalar_one()
            
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
        
        article = db.session.execute(db.select(Article).filter_by(id=id)).scalar_one_or_none()

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
        articles = Article.query.filter(Article.title.like(search))
        user = db.session.execute(db.select(User).filter_by(username=session['username'])).scalar()

        if articles:
            return render_template('articles.html',articles = articles,user=user)
        return render_template('articles.html')
                


@app.route('/like/<string:article_id>')
@login_required
def like(article_id):
    article = db.session.execute(db.select(Article).filter_by(id = article_id)).scalar()
    user = db.session.execute(db.select(User).filter_by(username = session['username'])).scalar()
    like = db.session.execute(db.select(Like).filter_by(author = user.id,article_id=article.id)).scalar()

    if not article:
        flash("there is no article like that",'danger')
    
    elif like:
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
    user = db.session.execute(db.select(User).filter_by(username=session['username'])).scalar()
    article = db.session.execute(db.select(Article).filter_by(id=article_id)).scalar_one()
    if request.method == 'POST' and form.validate():  
        comment = Comment(content=form.content.data , author= user.id ,article_id=article_id)
        db.session.add(comment)
        db.session.commit()
        flash('Comment added succesfully','success')
        return redirect(url_for('detail',id=article_id))
    else:
        return render_template('addcomment.html',form = form)



