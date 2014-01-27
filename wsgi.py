#!/usr/bin/env python

def run():
    import api
    from api.config import appfog_config

    config = appfog_config()
    if not config:
        from api.config import local_config
        config = local_config()

    app = api.create_app(app_name=__name__, config=config)
    api.register_app(app)
    app.run()

if __name__ == '__main__':
    run()