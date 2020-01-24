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

@app.route('/database/add_files.html')
@app.route('/database/add_files')
def database_add_files():
    return render_template('database_add_files.html')

