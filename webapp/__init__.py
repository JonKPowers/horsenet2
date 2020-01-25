import os

from flask import Flask

from . import horsenet, database

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY='dev')

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

    app.register_blueprint(database.bp)
    app.register_blueprint(horsenet.bp)
    app.add_url_rule('/', endpoint='index')

    return app

