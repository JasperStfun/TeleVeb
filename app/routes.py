# -*- coding: utf-8 -*-
import uuid
from flask import render_template, flash, redirect, request, url_for
from app import app, db, socketio
from app.forms import ChatForm, EmailEditForm, LoginForm, ProfileForm, RegistrationForm, UsernameEditForm
from app.forms import SearchForm
from flask_login import current_user, login_user, login_required, logout_user
from app.model import Message, User, Chat, UserArchive
from werkzeug.urls import url_parse
from flask_socketio import emit, join_room
from datetime import datetime
from werkzeug.utils import secure_filename
import os

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = User.query.filter(User.id == current_user.id).first()
    avatar = user.avatar
    return render_template('index.html', title='Home', current_user=current_user, avatar=avatar)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        file = form.avatar.data
        filename = str(uuid.uuid4()) + secure_filename(file.filename)
        file.save(os.path.join('app/static/', 'avatars/', filename))
        user = User(username=form.username.data, email=form.email.data, avatar=f'/static/avatars/{filename}')
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
                return render_template('welcome_to_chat.html', users=users, search_form=search_form,
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
        chat_existence = Chat.query.filter(
            (Chat.user_1_id == user_1.id) | (Chat.user_2_id == user_1.id)
        ).filter(
            (Chat.user_1_id == user_2.id) | (Chat.user_2_id == user_2.id)
        ).first()
        if chat_existence is None:
            chat = create_chat(user_1, user_2)
            chat_id = chat.id
        else:
            chat_id = chat_existence.id
        chat_form = ChatForm()
        all_messages = Message.query.filter(Message.message_chat_id == chat_id).all()
        return render_template('chat.html', user_1=user_1, user_2=user_2, chat_id=chat_id,
                               chat_form=chat_form, all_messages=all_messages)
    flash('Login or register')
    return redirect(url_for('login'))


def create_chat(user_1, user_2):
    unique_number =  uuid.uuid4()
    chat = Chat(user_1_id=user_1.id, user_2_id=user_2.id, unique_number=unique_number)
    db.session.add(chat)
    db.session.commit()
    return chat


@socketio.on('send message')
def handle_message(message, chat_id):
    if current_user.is_authenticated:
        chat_existence = Chat.query.filter(Chat.id == chat_id).first_or_404()
        message = str(message)
        send_user = current_user.id
        dt_now = datetime.now().strftime('%m.%d.%Y %H:%M:%S')
        content = Message(content=message, message_chat_id=chat_id,
                          send_user_id=send_user, published=dt_now)
        db.session.add(content)
        db.session.commit()
        dt_now = datetime.now().strftime('%d.%m.%Y %H:%M')
        message_info = f'{dt_now} {current_user.username}: {message}'
        emit('display message', message_info, room=chat_existence.unique_number)


@socketio.on('join')
def join(chat_id):
    chat_existence = Chat.query.filter(Chat.id == chat_id).first_or_404()
    room = chat_existence.unique_number
    join_room(room)


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
        email_edit_form = EmailEditForm()
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
    user = User.query.filter(User.id == current_user.id).first()
    user_archive = UserArchive(username=username_edit_form.username.data)
    user.username = username_edit_form.username.data
    db.session.add(user_archive)
    db.session.commit()
    flash('You have successfully changed your username!')
    return redirect(url_for('edit_profile', pk=pk))


def edit_email(current_user, email_edit_form, pk):
    user = User.query.filter(User.id == current_user.id).first()
    user.email = email_edit_form.email.data
    db.session.commit()
    flash('You have successfully changed your email!')
    return redirect(url_for('edit_profile', pk=pk))
