import functools
import os
from os import path

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
from werkzeug.utils import secure_filename

from flask_uploads import UploadSet, ALL
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import SubmitField

from webapp.add_files import add_file

bp = Blueprint('database', __name__, url_prefix='/database')

@bp.route('/')
def database_home():
    return render_template('database/database_home.html')

def allowed_filetype(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_UPLOAD_EXTENSIONS']

racefiles = UploadSet('racefiles', ALL)

class UploadForm(FlaskForm):
    racefile = FileField(validators=[FileRequired('Choose a file!')])
    submit = SubmitField('Upload')

@bp.route('/add_files', methods=['GET', 'POST'])
def database_add_files():
    form = UploadForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            for filename in request.files.getlist('racefile'):
                if not allowed_filetype(filename.filename):
                    flash(f'Filetype not allowed: {filename.filename}')
                else:
                    flash(f'Adding file: {filename.filename}')
                    add_file(filename)
        else:
            flash('validate_on_submit() failed')
        return redirect(url_for('database.database_add_files'))    

    return render_template('database/add_files.html', form=form)

@bp.route('/file_maintenance')
def database_file_maintenance():
    return render_template('database/file_maintenance.html')
