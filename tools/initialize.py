#!/usr/bin/env python

import api
import logging
from api.config import local_config
from api.security.models import Role
from api.security.models import User
from flask.ext.mongoengine import MongoEngine
from flask.ext.security.utils import encrypt_password

def _init_db(admin_email, admin_password):
    if len(User.objects):
        logging.error('There are Users in the database.  Clear the database before initializing.')
        return

    admin = User()
    admin.email = admin_email
    admin.password = encrypt_password(admin_password)
    admin.save()

    logging.info('Created admin user %s' % admin_email)

def init_app(admin_email, admin_password):
    app = create_app()

    with app.app_context():
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        _init_db(admin_email, admin_password)

def create_app():
    return api.create_app(app_name='console', config=local_config())
