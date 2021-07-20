# -*- coding: utf-8 -*-
import uuid
from flask import render_template, flash, redirect, request, url_for
from app import app, db, socketio
from app.forms import ChatForm, EmailEditForm, LoginForm, ProfileForm, RegistrationForm, UsernameEditForm, \
    PrivacyEditForm, CreatePublic
from app.forms import SearchForm
from flask_login import current_user, login_user, login_required, logout_user
from app.model import Message, User, Chat, UserArchive, Public_chat
from werkzeug.urls import url_parse
from flask_socketio import emit, join_room
from datetime import datetime
from werkzeug.utils import secure_filename, validate_arguments
import os
from PIL import Image, ImageOps, ImageDraw


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    user = User.query.filter(User.id == current_user.id).first()
    avatar = user.avatar
    form = CreatePublic()
    if form.validate_on_submit():
        create_public(user=user)
    return render_template('index.html', title='Home', current_user=current_user, avatar=avatar,
                           form=form)


@app.route('/friends/<username>')
@login_required
def add_friend(username):
    user = User.query.filter_by(username=username).first()
    if User is None:
        flash(f'User {username} not found.')
        return redirect(url_for('edit_profile', pk=user.id))
    if user == current_user:
        flash('You cannot friendship with yourself!')
        return redirect(url_for('edit_profile', pk=user.id))
    current_user.add_friend(user)
    db.session.commit()
    flash(f'Now you are friends with {username}')
    return redirect(url_for('edit_profile', pk=user.id))


@app.route('/remove_friend/<username>')
@login_required
def del_friend(username):
    user = User.query.filter_by(username=username).first()
    if User is None:
        flash(f'User {username} not found.')
        return redirect(url_for('profile', pk=user.id))
    if user == current_user:
        flash('You cannot delete yourself!')
        return redirect(url_for('profile', pk=user.id))
    current_user.del_friend(user)
    db.session.commit()
    flash(f'{username} not your friend anymore')
    return redirect(url_for('edit_profile', pk=user.id))


@app.route('/black/<username>')
@login_required
def add_black_user(username):
    user = User.query.filter_by(username=username).first()
    if User is None:
        flash(f'User {username} not found.')
        return redirect(url_for('edit_profile', pk=user.id))
    if user == current_user:
        flash('You cannot blocked yourself!')
        return redirect(url_for('edit_profile', pk=user.id))
    current_user.add_black_user(user)
    db.session.commit()
    flash(f'Now {username} in black list')
    return redirect(url_for('edit_profile', pk=user.id))


@app.route('/remove_black/<username>')
@login_required
def del_black_user(username):
    user = User.query.filter_by(username=username).first()
    if User is None:
        flash(f'User {username} not found.')
        return redirect(url_for('profile', pk=user.id))
    if user == current_user:
        flash('You cannot delete yourself!')
        return redirect(url_for('profile', pk=user.id))
    current_user.del_black_user(user)
    db.session.commit()
    flash(f'{username} not in black list anymore')
    return redirect(url_for('profile', pk=user.id))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        avatar = set_avatar(form)
        user = User(username=form.username.data, email=form.email.data, avatar=avatar)
        user_archive = UserArchive(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.add(user_archive)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Регистрация', form=form)


def set_avatar(form):
    file = form.avatar.data
    if file is not None:
        filename = str(uuid.uuid4()) + secure_filename(file.filename)
        file.save(os.path.join('app/static/', 'avatars/', filename))
        edit_download_image(filename)
        avatar = f'/static/avatars/{filename}.png'
    else:
        avatar = f'https://api.multiavatar.com/{form.username.data}.png'
    return avatar


def edit_download_image(filename):
    image = Image.open(f'app/static/avatars/{filename}')
    size = (200, 200)
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    image = image.resize(size)
    output = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)
    output.thumbnail(size, Image.ANTIALIAS)
    output.save(f'app/static/avatars/{filename}.png')
    os.remove(f'app/static/avatars/{filename}')


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


@app.route('/welcome_to_public/', methods=['GET', 'POST'])
def welcome_to_public():
    if current_user.is_authenticated:
        users = User.query.filter(User.username != current_user.username).all()
        public = Public_chat.query.filter(Public_chat.id)
        search_form = SearchForm()
        if search_form.validate_on_submit():
            content = search_form.search.data
            search_result = User.query.filter(User.username == content).first()
            if search_result is not None:
                search_result = search_result.username
                return render_template('welcome_to_public.html', users=users, search_form=search_form,
                                       search_result=search_result)
            else:
                flash('User not found')
                return render_template('welcome_to_public.html',
                                       users=users, search_form=search_form)
        else:
            return render_template('welcome_to_public.html',
                                   users=users, search_form=search_form, public=public)
    flash('Login or register')
    return redirect(url_for('login'))


@app.route('/welcome_to_public/<pk>', methods=['GET', 'POST'])
def public_chat(pk):
    if current_user.is_authenticated:
        user = current_user
        public = Public_chat.query.filter(Public_chat.id == pk).first_or_404()
        if public is None:
            public = create_public(user, public)
            public_id = public.id
        else:
            public_id = public.id
        public_form = ChatForm()
        all_messages = Message.query.filter(Message.public_message_id == public_id).all()
        return render_template('public_chat.html', user=user, public=public, public_id=public_id,
                               public_form=public_form, all_messages=all_messages)
    flash('Login or register')
    return redirect(url_for('login'))


def create_public(user, public):
    is_uniq_number_exists = True
    while is_uniq_number_exists:
        unique_number = str(uuid.uuid4())
        is_uniq_number_exists = Chat.query.filter(Chat.unique_number == unique_number).first()
    public = Public_chat(users=user.id, unique_number=unique_number)
    db.session.add(public)
    db.session.commit()
    return public


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
        chat = Chat.query.filter(
            (Chat.user_1_id == user_1.id) | (Chat.user_2_id == user_1.id)
        ).filter(
            (Chat.user_1_id == user_2.id) | (Chat.user_2_id == user_2.id)
        ).first()

        if user_2.is_blacked(user_1):
            flash('You in black list')
            return redirect(url_for('edit_profile', pk=user_2.id))

        if chat is None:
            chat = create_chat(user_1, user_2, )
            chat_id = chat.id
        else:
            chat_id = chat.id
        chat_form = ChatForm()
        all_messages = Message.query.filter(Message.message_chat_id == chat_id).all()
        return render_template('chat.html', user_1=user_1, user_2=user_2, chat_id=chat_id,
                               chat_form=chat_form, all_messages=all_messages)
    flash('Login or register')
    return redirect(url_for('login'))


def create_chat(user_1, user_2):
    is_uniq_number_exists = True
    while is_uniq_number_exists:
        unique_number = str(uuid.uuid4())
        is_uniq_number_exists = Chat.query.filter(Chat.unique_number == unique_number).first()
    chat = Chat(user_1_id=user_1.id, user_2_id=user_2.id, unique_number=unique_number)
    db.session.add(chat)
    db.session.commit()
    return chat


@socketio.on('send message')
def handle_message(message, chat_id):
    if current_user.is_authenticated:
        chat = Chat.query.filter(Chat.id == chat_id).first_or_404()
        send_user = current_user.id
        content = Message(content=message, message_chat_id=chat_id,
                          send_user_id=send_user, published=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        db.session.add(content)
        db.session.commit()
        message_info = (
            f'{content.published.strftime("%Y.%m.%d %H:%M")}<br>'
            f'<img src="{content.send_user_username.avatar}" height="35" width="35">'
            f'{content.send_user_username.username}: {message}')
        emit('display message', message_info, room=chat.unique_number)


@socketio.on('join')
def join(chat_id):
    chat = Chat.query.filter(Chat.id == chat_id).first_or_404()
    room = chat.unique_number
    join_room(room)


@socketio.on('join_public')
def join_public(public_id):
    public = Public_chat.query.filter(Public_chat.id == public_id).first_or_404()
    room = public.unique_number
    join_room(room)


@app.route('/profile/<pk>', methods=['GET', 'POST'])
def user_profile(pk):
    if current_user.is_authenticated:
        user = User.query.filter(User.id == pk).first()
        profile_form = ProfileForm()
        profile_form.username.data = current_user.username
        profile_form.email.data = current_user.email
        if current_user.id == user.id:
            return render_template('user_profile.html',
                                   current_user=current_user, profile_form=profile_form, user=user)
        if current_user.id != user.id:
            if user.privacy == 'all':
                return render_template('user_profile.html',
                                       current_user=current_user, profile_form=profile_form, user=user)
            if user.privacy == 'nobody':
                flash('User has restricted access to his profile')
                return redirect(url_for('index'))
            if user.privacy == 'friends':
                if user.is_friend(current_user):
                    return render_template('user_profile.html',
                                           current_user=current_user, profile_form=profile_form, user=user)
                else:
                    flash('User has restricted access to his profile')
                    return redirect(url_for('index'))
    flash('Login or register')
    return redirect(url_for('login'))


@app.route('/edit_profile/<pk>', methods=['GET', 'POST'])
def edit_profile(pk):
    if current_user.is_authenticated:
        username_edit_form = UsernameEditForm()
        email_edit_form = EmailEditForm()
        privacy_edit_form = PrivacyEditForm()
        if username_edit_form.validate_on_submit():
            edit_username(current_user, username_edit_form, pk)
        if email_edit_form.validate_on_submit():
            edit_email(current_user, email_edit_form, pk)
        if privacy_edit_form.validate_on_submit():
            edit_privacy(current_user, privacy_edit_form, pk)
        else:
            username_edit_form.username.data = current_user.username
            email_edit_form.email.data = current_user.email
        return render_template('edit_profile.html',
                               current_user=current_user, username_edit_form=username_edit_form,
                               email_edit_form=email_edit_form, privacy_edit_form=privacy_edit_form)
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


def edit_privacy(current_user, privacy_edit_form, pk):
    user = User.query.filter(User.id == current_user.id).first()
    user.privacy = privacy_edit_form.privacy.data
    db.session.commit()
    flash('Privacy settings accept')
    return redirect(url_for('edit_profile', pk=pk))
