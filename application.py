from api.security.models import Role, User
from flask import jsonify
from flask import Flask
from flask.ext.mongoengine import MongoEngine
from flask.ext.security import Security
from flask.ext.security import MongoEngineUserDatastore
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import SecurityError

allowed_methods = (
    'GET',
    'HEAD',
    'POST',
    'DELETE',
    'PUT',
    'PATCH',
    'OPTIONS'
)
bodyless_methods = ('GET', 'HEAD', 'OPTIONS', 'DELETE')


class CorsHeadersMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        def cors_start_response(status, headers, exc_info=None):
            headers.append(('Access-Control-Allow-Origin', '*'))
            headers.append(('Access-Control-Allow-Methods', ', '.join(allowed_methods)))
            headers.append(('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept'))
            return start_response(status, headers, exc_info)

        return self.app(environ, cors_start_response)


class HTTPMethodOverrideMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        method = environ.get('HTTP_X_HTTP_METHOD_OVERRIDE', '').upper()
        if method in allowed_methods:
            method = method.encode('ascii', 'replace')
            environ['REQUEST_METHOD'] = method
            if method in bodyless_methods:
                environ['CONTENT_LENGTH'] = '0'
        return self.app(environ, start_response)


def appfog_config():
    import json
    import os

    services = json.loads(os.environ.get('VCAP_SERVICES', '{}'))
    if not services:
        return None

    config = {}

    # general app config
    config['DEBUG'] = False

    # db config
    db_config = services['mongodb-1.8'][0]['credentials']
    if not db_config:
        raise Exception("Invalid configuration:  Where is Mongo?")

    config['MONGODB_DB'] = db_config['db']
    config['MONGODB_USERNAME'] = db_config['username']
    config['MONGODB_PASSWORD'] = db_config['password']
    config['MONGODB_HOST'] = db_config['hostname']
    config['MONGODB_PORT'] = db_config['port']

    # security
    config['SECRET_KEY'] = services['flask-secret-key']
    config['SECURITY_PASSWORD_HASH'] = services['flask-security-password-hash']
    config['SECURITY_PASSWORD_SALT'] = services['flask-security-password-salt']

    return config

def local_config():
    config = {}

    # general app config
    config['DEBUG'] = True

    # db config
    config['MONGODB_DB'] = 'localdb'
    config['MONGODB_USERNAME'] = ''
    config['MONGODB_PASSWORD'] = ''
    config['MONGODB_HOST'] = 'localhost'
    config['MONGODB_PORT'] = 27017

    # security
    config['SECRET_KEY'] = 'secret-key'
    config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
    config['SECURITY_PASSWORD_SALT'] = 'secret-salt'

    return config

def create_app(app_name, config, **kwargs):
    """
    Create a Flask app for a REST API.  
    Uses MongoDB and JSON.
    """
    app = Flask(app_name, **kwargs)
    app.config.update(config)

    # middleware
    app.wsgi_app = HTTPMethodOverrideMiddleware(app.wsgi_app)
    if app.config['DEBUG'] == True:
        app.wsgi_app = CorsHeadersMiddleware(app.wsgi_app)

    # error handling
    # see http://flask.pocoo.org/snippets/83
    def handle_api_error(ex):
        response = jsonify(message=str(ex))
        response.status_code = (ex.code
                                if isinstance(ex, HTTPException)
                                else 500)
        return response

    for code in default_exceptions.iterkeys():
        app.error_handler_spec[None][code] = handle_api_error

    # security
    if not app.config['SECRET_KEY']:
        raise SecurityError(description="Invalid configuration:  Don't forget your keys")

    if not app.config['SECURITY_PASSWORD_HASH'] \
        or app.config['SECURITY_PASSWORD_HASH'] == 'plaintext':
        raise SecurityError(description="Invalid configuration:  Hash it out")

    if not app.config['SECURITY_PASSWORD_SALT']:
        raise SecurityError(description="Invalid configuration:  Pass the salt")

    db = MongoEngine(app)
    user_datastore = MongoEngineUserDatastore(db, User, Role)
    security = Security(app, user_datastore)

    return app

