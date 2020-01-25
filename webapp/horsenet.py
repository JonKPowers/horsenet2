from flask import Blueprint, render_template

bp = Blueprint('horsenet', __name__)

@bp.route('/')
@bp.route('/index.html')
def index():
    return render_template('index.html')
