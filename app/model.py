from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    user = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(21), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(28), nullable=False)


class UserPicture(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    pictures = db.Column(db.String)


class Message(db.Model):
    message_id = db.Column(db.Integer, primary_key=True)
    send_user = db.Column(db.Integer)
    rec_user = db.Column(db.Integer)
    content = db.Column(db.Text, nullable=True)
    published = db.Column(db.DateTime, nullable=False)

class Chat(db.Model):
    chat_id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, primary_key=True)