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
    logging.info('Created admin user %s' % admin.email)

    role = Role()
    role.name = 'Super Admin'
    role.description = 'The Super Admin role is for configuring application settings'
    role.save()
    logging.info('Created %s role' % role.name)

    admin.roles = [role]
    admin.save()
    logging.info('Added %s role to %s' % (role.name, admin.email))

def setup_logging():
    fmt = "%(asctime)s %(levelname)s %(filename)s:%(lineno)d:%(funcName)s" \
          "    %(message)s"

    logging.basicConfig(format=fmt)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

def create_app():
    return api.create_app(app_name='console', config=local_config())

def init_app(admin_email, admin_password):
    app = create_app()

    with app.app_context():
        setup_logging()

        _init_db(admin_email, admin_password)

