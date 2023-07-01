from wtforms import Form, StringField, TextAreaField, PasswordField, validators



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


class CommentForm(Form):
    content = TextAreaField('content')