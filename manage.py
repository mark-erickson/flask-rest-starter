#!/usr/bin/env python

def init_app(args):
    from tools.initialize import init_app
    init_app(admin_email=args.email,
             admin_password=args.password)

def run_db(args):
    import os
    from subprocess import Popen

    try:
        print "Starting up database..."
        p_mongod = Popen(['mongod', '--config', 'tools/mongod-dev.conf'])
        p_mongod.communicate()
    except KeyboardInterrupt:
        print "Shutting down database..."

def run_web(args):
    import wsgi

    wsgi.run()

def setup_logging(name=None):
    import logging

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    import argparse

    setup_logging('root')

    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest='command', help='command help')
    
    command = commands.add_parser('init', 
        help='initialize the application data')
    command.set_defaults(func=init_app)
    command.add_argument('email', help="The admin user's email address")
    command.add_argument('password', help="The admin user's password")

    command = commands.add_parser('db', 
        help='run the development database')
    command.set_defaults(func=run_db)

    command = commands.add_parser('web', 
        help='run the development webserver')
    command.set_defaults(func=run_web)

    args = parser.parse_args()
    args.func(args)

