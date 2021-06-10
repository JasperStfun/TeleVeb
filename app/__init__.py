from flask import Flask
from app.model import db
app = Flask(__name__)
app.config.from_pyfile('config.py')
db.init_app(app)
from app import routes

