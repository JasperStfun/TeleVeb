from flask.app import Flask
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.fields.simple import TextAreaField
from flask_wtf.file import FileField
from wtforms.validators import DataRequired, Email, EqualTo, Required
from wtforms.validators import ValidationError, Length
from app.model import User, UserArchive
from wtforms.fields.html5 import EmailField, SearchField
from flask_login import current_user
from wtforms.fields import SelectField


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
    avatar = FileField('Avatar', render_kw={"class": "form-control"})
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
    submit = SubmitField('Search',
                         render_kw={"class": "btn btn-outline-primary"})


class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[Required()],
                           render_kw={"class": "form-control"})
    email = EmailField('Email', validators=[DataRequired(), Email()],
                       render_kw={"class": "form-control"})
    password = PasswordField('Password', validators=[DataRequired(),
                                                     Length(min=4, max=16)],
                             render_kw={"class": "form-control"})
    password_2 = PasswordField(
        'Repeat password', validators=[DataRequired(), EqualTo('password')],
        render_kw={"class": "form-control"})
    submit = SubmitField('Change',
                         render_kw={"class": "btn btn-outline-primary"})

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email adress.')


class UsernameEditForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()],
                           render_kw={"class": "form-control"})
    submit = SubmitField('Change',
                         render_kw={"class": "btn btn-outline-primary"})

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        user_archive = UserArchive.query.filter_by(username=username.data).first()
        if user == current_user:
            raise ValidationError('The username is the same as the current one')
        if user is not None or user_archive is not None:
            raise ValidationError('Please use a different username.')


class EmailEditForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()],
                       render_kw={"class": "form-control"})
    submit = SubmitField('Change',
                         render_kw={"class": "btn btn-outline-primary"})

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email adress.')


class PrivacyEditForm(FlaskForm):
    privacy = SelectField(u'Настройка приватности',
                          choices=[('all', 'Все'), ('friends', 'только друзья'),
                          ('nobody', 'никто')])
    submit = SubmitField('Change',
                         render_kw={"class": "btn btn-outline-primary"})

