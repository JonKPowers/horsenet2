import functools
import os

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/home/jkpowers/data/python/horsenet_2/horse_data'
ALLOWED_EXTENSIONS = {'1', '2', '3', '4', '5', '6', 'drf'}

bp = Blueprint('database', __name__, url_prefix='/database')

@bp.route('/')
def database_home():
    return render_template('database/database_home.html')

def allowed_filetype(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/add_files', methods=['GET', 'POST'])
def database_add_files():
    # Set upload folder in app configuration
    current_app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part in request')
            return redirect(request.url)
        file = request.files['file']

        # Handle if user does not select a file
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        elif not allowed_filetype(file.filename):
            flash('File type not allowed')
        elif file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            flash('File saved')
            return redirect(url_for('database.database_add_files'))
        else:
            flash('Hit the end--something went wrong')

    return render_template('database/add_files.html')

@bp.route('/file_maintenance')
def database_file_maintenance():
    return render_template('database/file_maintenance.html')
