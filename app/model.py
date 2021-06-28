from datetime import datetime
from enum import unique

from sqlalchemy.orm import relationship
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(21), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(28))
    role = db.Column(db.String(10), default='user')
    message = db.relationship('Message', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User: {self.username} id: {self.id}>'


class Message(db.Model):
    __tablename__ = 'message'
    message_id = db.Column(db.Integer, primary_key=True)
    send_user_name = db.Column(db.String, db.ForeignKey('user.username'))
    content = db.Column(db.Text, nullable=True)
    published = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return f'{self.send_user_name}: {self.content}'


class UserPicture(db.Model):
    __tablename__ = 'user_picture'
    user_id_pic = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    pictures = db.Column(db.String)


class Chat(db.Model):
    __tablename__ = 'chat'
    chat_id = db.Column(db.Integer, primary_key=True)
    user_1_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_2_id = db.Column(db.Integer, db.ForeignKey('user.id'))
