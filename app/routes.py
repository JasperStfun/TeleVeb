# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, request, url_for
from app import app, db
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, login_required, logout_user
from app.model import User, Chat
from werkzeug.urls import url_parse


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/welcome_to_chat/', methods = ['GET', 'POST'])
def welcome_to_chat():
    if current_user.is_authenticated:
        users = User.query.order_by(User.username).all()
        return render_template('welcome_to_chat.html', users=users)
    flash('Login or register')
    return redirect(url_for('login'))


@app.route('/welcome_to_chat/<pk>', methods = ['GET', 'POST'])
def chat(pk):
    if current_user.is_authenticated:
        user_1 = current_user
        user_2 = User.query.get(pk)
        chat_check_1 = Chat.query.filter(Chat.user_1_id==user_1.id, Chat.user_2_id==user_2.id).first()
        chat_check_2 = Chat.query.filter(Chat.user_1_id==user_2.id, Chat.user_2_id==user_1.id).first()
        if chat_check_1 is None and chat_check_2 is None:
            create_chat(user_1, user_2)
        
        return render_template('chat.html', user_1=user_1, user_2=user_2)
    flash('Login or register')
    return redirect(url_for('login'))

def create_chat(user_1, user_2):
    chat = Chat(user_1_id=user_1.id, user_2_id=user_2.id)
    db.session.add(chat)
    db.session.commit()