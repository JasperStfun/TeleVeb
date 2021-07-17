from datetime import datetime
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

black_list = db.Table('black_list',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('banned_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(21), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(300))
    role = db.Column(db.String(10), default='user')
    avatar = db.Column(db.String(150),  unique=True)
    privacy = db.Column(db.String, default='all')
    message = db.relationship('Message', backref='author', lazy='dynamic')
    friendlist = db.relationship('User', secondary=friends,
        primaryjoin=(friends.c.user_id == id),
        secondaryjoin=(friends.c.friend_id == id),
        backref=db.backref('friends', lazy='dynamic'), lazy='dynamic')
    blacklist_user = db.relationship('User', secondary=black_list,
        primaryjoin=(black_list.c.user_id == id),
        secondaryjoin=(black_list.c.banned_id == id),
        backref=db.backref('black_list', lazy='dynamic'), lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def add_friend(self, user):
        if not self.is_friend(user):
            self.friendlist.append(user)

    def del_friend(self, user):
        if self.is_friend(user):
            self.friendlist.remove(user)
    
    def is_friend(self, user):
        return self.friendlist.filter(
            friends.c.friend_id == user.id).count() > 0
    
    def add_black_user(self, user):
        if not self.is_blacked(user):
            self.blacklist_user.append(user)

    def del_black_user(self, user):
        if self.is_blacked(user):
            self.blacklist_user.remove(user)
    
    def is_blacked(self, user):
        return self.blacklist_user.filter(
            black_list.c.banned_id == user.id).count() > 0
    
    def __repr__(self):
        return f'<User: {self.username} id: {self.id}, avatar: {self.avatar}>'


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    send_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    send_user_username = db.relationship('User', lazy='select')
    content = db.Column(db.Text, nullable=True)
    published = db.Column(db.DateTime, index=True)
    message_chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'))

    def __repr__(self):
        return (f'<Message_id: {self.id} Chat_id: {self.message_chat_id}'
                f' Username: {self.send_user_username}'
                f' Content: {self.content} Published: {self.published}>')


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

