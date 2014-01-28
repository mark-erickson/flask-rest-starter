#!/usr/bin/env python
import application
import api

def run():
    config = application.appfog_config()
    if not config:
        config = application.local_config()

    app = application.create_app(app_name=__name__, config=config)
    api.register_app(app)
    app.run()

if __name__ == '__main__':
    run()