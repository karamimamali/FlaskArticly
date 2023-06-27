from flask import render_template,flash, redirect, url_for, session, request
from passlib.hash import sha256_crypt
from functools import wraps
from forms import RegisterForm , LogInForm ,ArticleForm
from main import app, db 
from models import Articles , Users



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
                