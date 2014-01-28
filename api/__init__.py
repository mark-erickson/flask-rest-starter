def register_app(app):
    from security import RolesView

    RolesView.register(app, route_prefix='/api/1')
