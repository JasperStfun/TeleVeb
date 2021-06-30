import os

basedir = os.path.abspath(os.path.dirname(__file__))
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = 'postgresql://sfozwgdh:bnCnsLzG_RZ36v8uq6mSZtS6iNHvTDaq@hattie.db.elephantsql.com/sfozwgdh'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
