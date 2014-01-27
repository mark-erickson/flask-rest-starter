from flask import jsonify
from flask import Flask
from flask.ext.mongoengine import MongoEngine
from flask.ext.security import Security
from flask.ext.security import MongoEngineUserDatastore
from middleware import HTTPMethodOverrideMiddleware
from security.models import Role, User
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import SecurityError

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
        from middleware import CorsHeadersMiddleware
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

def register_app(app):
    from members import MembersView

    MembersView.register(app, route_prefix='/api/1')
