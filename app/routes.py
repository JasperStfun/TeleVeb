# -*- coding: utf-8 -*-
from app import app

@app.route('/')
@app.route('/index')
def index():
    return 'Simple_text_project, ТЕСТ_РУ'