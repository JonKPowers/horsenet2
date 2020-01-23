from flask import render_template
from webapp import app

@app.route('/')
@app.route('/index.html')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/database')
@app.route('/database.html')
def database_page():
    return render_template('database.html')


