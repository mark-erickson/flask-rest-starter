import json
import os

from api import accounts
from eve import Eve
from eve.auth import TokenAuth
from flask import redirect
from werkzeug.security import check_password_hash


def config_common(config):

    config['URL_PREFIX'] = 'api'


def config_domain(config):

    config['DOMAIN'] = {
        'accounts': accounts.endpoint
    }


def find_appfog_config():
    return json.loads(os.environ.get('VCAP_SERVICES', '{}'))

def config_appfog(config, appfog_config):
    if not services:
        return

    # general app config
    config['DEBUG'] = False

    # db config
    db_config = appfog_config['mongodb-1.8'][0]['credentials']
    if not db_config:
        raise Exception("Invalid configuration:  Where is Mongo?")

    config['MONGODB_DB'] = db_config['db']
    config['MONGODB_USERNAME'] = db_config['username']
    config['MONGODB_PASSWORD'] = db_config['password']
    config['MONGODB_HOST'] = db_config['hostname']
    config['MONGODB_PORT'] = db_config['port']


def config_local(config):
    # general app config
    config['DEBUG'] = True

    # db config
    config['MONGODB_DB'] = 'localdb'
    config['MONGODB_USERNAME'] = ''
    config['MONGODB_PASSWORD'] = ''
    config['MONGODB_HOST'] = 'localhost'
    config['MONGODB_PORT'] = 27017


def get_config():

    config = {}

    config_common(config)
    config_domain(config)

    appfog_config = find_appfog_config()
    if appfog_config:
        config_appfog(config, appfog_config)
    else:
        config_local(config)

    return config


class RolesAuth(TokenAuth):
    def check_auth(self, username, password, allowed_roles, resource, method):
        # use Eve's own db driver; no additional connections/resources are used
        accounts = app.data.driver.db['accounts']
        lookup = {'username': username}
        if allowed_roles:
            # only retrieve a user if his roles match ``allowed_roles``
            lookup['roles'] = {'$in': allowed_roles}
        account = accounts.find_one(lookup)
        
        return account

def index():
    return app.send_static_file('index.html')

def create_app():
    """
    Create an Eve Flask api application
    """
    dirname = os.path.dirname(os.path.realpath(__file__))

    app = Eve(
        auth=RolesAuth, 
        settings=get_config(),
        static_url_path='',
        static_folder= dirname + '/static'
    )

    app.add_url_rule('/', 'index', index)

    return app

app = create_app()