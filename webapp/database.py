import functools

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for

bp = Blueprint('database', __name__, url_prefix='/database')

@bp.route('/')
def database_home():
    return render_template('database/database_home.html')

@bp.route('/add_files')
def database_add_files():
    return render_template('database/add_files.html')

@bp.route('/file_maintenance')
def database_file_maintenance():
    return render_template('database/file_maintenance.html')

