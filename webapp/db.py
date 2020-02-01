from couchbase.cluster import Cluster
from couchbase.cluster import PasswordAuthenticator

from flask import current_app, g

def get_db():
    if 'db' not in g:
        user = current_app.config['DATABASE_LOGIN']
        password = current_app.config['DATABASE_PASSWORD']
        if current_app.config['TESTING']:
            bucket = current_app.config['DATABASE_TEST_BUCKET']
        else:
            bucket = current_app.config['DATABASE_PROD_BUCKET']
        cluster = Cluster(current_app.config['DATABASE_CLUSTER'])
        authenticator = PasswordAuthenticator(user, password)

        cluster.authenticate(authenticator)
        g.db = cluster.open_bucket(current_app.config['DATABASE_BUCKET'])

    return g.db

def close_db():
    db = g.pop('db', None)

    if db is not None:
        db.close()
