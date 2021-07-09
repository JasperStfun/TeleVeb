from datetime import datetime
from enum import unique
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


friends = db.Table('friends',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('friend_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(21), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(300))
    role = db.Column(db.String(10), default='user')
    message = db.relationship('Message', backref='author', lazy='dynamic')
    friendlist = db.relationship('User', secondary=friends,
        primaryjoin=(friends.c.user_id == id),
        secondaryjoin=(friends.c.friend_id == id),
        backref=db.backref('friends', lazy='dynamic'), lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def add_friend(self, user):
        if not self.is_friend(user):
            self.friendlist(user)

    def del_friend(self, user):
        if self.is_friend(user):
            self.friendlist(user)
    
    def is_friend(self, user):
        return self.friendlist.filter(
            friends.c.friend_id == user.id).count() > 0

    def __repr__(self):
        return f'<User: {self.username} id: {self.id}>'


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    send_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    send_user_username = db.relationship('User', backref='user', lazy='select')
    content = db.Column(db.Text, nullable=True)
    published = db.Column(db.DateTime, index=True, default=datetime.now())
    message_chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'))

    def __repr__(self):
        return (f'<Message_id: {self.id} Chat_id: {self.message_chat_id}'
                f' Username: {self.send_user_username}'
                f' Content: {self.content}>')


class UserPicture(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    pictures = db.Column(db.String)


class Chat(db.Model):
    __table_args__ = (db.UniqueConstraint('user_1_id', 'user_2_id'),)
    id = db.Column(db.Integer, primary_key=True)
    unique_number = db.Column(db.String, nullable=False, unique=True)
    user_1_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_2_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return (f'<Chat: {self.id} user_1_id: '
                f'{self.user_1_id} user_2_id: {self.user_2_id}>')


class UserArchive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(21), nullable=False, unique=True)

