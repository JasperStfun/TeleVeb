# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, request, url_for
from app import app, db
from app.forms import ChatForm, EmailEditForm, LoginForm, ProfileForm, RegistrationForm, UsernameEditForm
from app.forms import SearchForm
from flask_login import current_user, login_user, login_required, logout_user
from app.model import Message, User, Chat, UserArchive
from werkzeug.urls import url_parse


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home', current_user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user_archive = UserArchive(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.add(user_archive)
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


@app.route('/welcome_to_chat/', methods=['GET', 'POST'])
def welcome_to_chat():
    if current_user.is_authenticated:
        users = User.query.filter(User.username != current_user.username).all()
        search_form = SearchForm()
        if search_form.validate_on_submit():
            content = search_form.search.data
            search_result = User.query.filter(User.username == content).first()
            if search_result is not None:
                search_result = search_result.username
                return render_template('welcome_to_chat.html',users=users, search_form=search_form,
                                    search_result=search_result)
            else:
                flash('User not found')
                return render_template('welcome_to_chat.html',
                                   users=users, search_form=search_form)
        else:
            return render_template('welcome_to_chat.html',
                                   users=users, search_form=search_form)
    flash('Login or register')
    return redirect(url_for('login'))


@app.route('/welcome_to_chat/<pk>', methods=['GET', 'POST'])
def chat(pk):
    if current_user.is_authenticated:
        user_1 = current_user
        user_2 = User.query.filter(User.id == pk).first_or_404()
        chat_check = Chat.query.filter(
            (Chat.user_1_id == user_1.id) | (Chat.user_2_id == user_1.id)
        ).filter(
            (Chat.user_1_id == user_2.id) | (Chat.user_2_id == user_2.id)
        ).first()
        if chat_check is None:
            chat = create_chat(user_1, user_2)
            chat = chat.id
        else:
            chat = chat_check.id
        chat_form = ChatForm()
        if chat_form.validate_on_submit():
            content = chat_form.user_message.data
            message = Message(send_user_id=user_1.id, content=content,
                              message_chat_id=chat)
            db.session.add(message)
            db.session.commit()
            return redirect(url_for('chat', pk=pk))
        all_messages = Message.query.filter(Message.message_chat_id == chat).all()
        return render_template('chat.html', user_1=user_1, user_2=user_2,
                               chat_form=chat_form, all_messages=all_messages)
    flash('Login or register')
    return redirect(url_for('login'))


def create_chat(user_1, user_2):
    chat = Chat(user_1_id=user_1.id, user_2_id=user_2.id)
    db.session.add(chat)
    db.session.commit()
    return chat


@app.route('/profile/<pk>', methods=['GET', 'POST'])
def user_profile(pk):
    if current_user.is_authenticated:
        profile_form = ProfileForm()
        profile_form.username.data = current_user.username
        profile_form.email.data = current_user.email
        return render_template('user_profile.html',
                               current_user=current_user, profile_form=profile_form)
    flash('Login or register')
    return redirect(url_for('login'))

@app.route('/edit_profile/<pk>', methods=['GET', 'POST'])
def edit_profile(pk):
    if current_user.is_authenticated:
        username_edit_form = UsernameEditForm()
        email_edit_form= EmailEditForm()
        if username_edit_form.validate_on_submit():
            edit_username(current_user, username_edit_form, pk)
        if email_edit_form.validate_on_submit():
            edit_email(current_user, email_edit_form, pk)
        else:
            username_edit_form.username.data = current_user.username
            email_edit_form.email.data = current_user.email
        return render_template('edit_profile.html',
                               current_user=current_user, username_edit_form=username_edit_form,
                               email_edit_form=email_edit_form)
    flash('Login or register')
    return redirect(url_for('login'))

def edit_username(current_user, username_edit_form, pk):
    user = User.query.filter(User.id==current_user.id).first()
    user_archive = UserArchive(username=username_edit_form.username.data)
    user.username = username_edit_form.username.data
    db.session.add(user_archive)
    db.session.commit()
    flash('You have successfully changed your username!')
    return redirect(url_for('edit_profile', pk=pk))

def edit_email(current_user, email_edit_form, pk):
    user = User.query.filter(User.id==current_user.id).first()
    user.email = email_edit_form.email.data
    db.session.commit()
    flash('You have successfully changed your email!')
    return redirect(url_for('edit_profile', pk=pk))