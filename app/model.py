from datetime import datetime
from app import db


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(21), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(28), nullable=False)
    role = db.Column(db.String(10))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return f'<User: {self.nickname} id: {self.user_id}>'


class Message(db.Model):
    message_id = db.Column(db.Integer, primary_key=True)
    send_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    rec_user = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    content = db.Column(db.Text, nullable=True)
    published = db.Column(db.DateTime, index=True, default=datetime.utcnow)


class UserPicture(db.Model):
    user_id_pic = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    pictures = db.Column(db.String)


class Chat(db.Model):
    chat_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
