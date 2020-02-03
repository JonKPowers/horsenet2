import os

from flask import Flask
from flask_uploads import configure_uploads, patch_request_class

from . import horsenet, database, app_settings
from .database import racefiles

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
            SECRET_KEY='dev',
            DATABASE_CLUSTER = 'couchbase://localhost', 
            DATABASE_LOGIN = 'horsenet', 
            DATABASE_PASSWORD = 'ABCABC123', 
            DATABASE_PROD_BUCKET = 'horsenet_prod', 
            DATABASE_BUCKET = 'horsenet_testing', 
            UPLOAD_FOLDER=app_settings.UPLOAD_FOLDER,
            ALLOWED_UPLOAD_EXTENSIONS=app_settings.ALLOWED_UPLOAD_EXTENSIONS,
            UPLOADED_RACEFILES_DEST = '/data/python/horsenet_2/horse_data'
    )

    # Load the instance config (if present) when not testing
    # and load the test config if passed in
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # Make sure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Setup flask-uploads configuration
    configure_uploads(app, racefiles)
    patch_request_class(app)

    app.register_blueprint(database.bp)
    app.register_blueprint(horsenet.bp)
    app.add_url_rule('/', endpoint='index')

    return app

