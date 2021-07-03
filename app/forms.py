from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms.validators import ValidationError, Length
from app.model import User
from wtforms.fields.html5 import EmailField, SearchField


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()],
                           render_kw={"class": "form-control"})
    password = PasswordField('Password', validators=[DataRequired(),
                             Length(min=4, max=16)],
                             render_kw={"class": "form-control"})
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In',
                         render_kw={"class": "btn btn-outline-primary"})


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()],
                           render_kw={"class": "form-control"})
    email = EmailField('Email', validators=[DataRequired(), Email()],
                       render_kw={"class": "form-control"})
    password = PasswordField('Password', validators=[DataRequired(),
                             Length(min=4, max=16)],
                             render_kw={"class": "form-control"})
    password_2 = PasswordField(
        'Repeat password', validators=[DataRequired(), EqualTo('password')],
        render_kw={"class": "form-control"})
    submit = SubmitField('Register',
                         render_kw={"class": "btn btn-outline-primary"})

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email adress.')


class ChatForm(FlaskForm):
    user_message = TextAreaField('New Message', validators=[DataRequired()],
                                 render_kw={"class": "form-control"})
    submit = SubmitField('Send',
                         render_kw={"class": "btn btn-outline-primary"})


class SearchForm(FlaskForm):
    search = SearchField('Search', validators=[DataRequired()],
                         render_kw={"class": "form-control"})

