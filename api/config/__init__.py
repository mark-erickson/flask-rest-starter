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
