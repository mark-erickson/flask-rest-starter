from api.security.models import Role
from flask import jsonify
from flask.ext.classy import FlaskView
from flask.ext.security import login_required

class RolesView(FlaskView):
    decorators = [login_required]

    def index(self):        
        return jsonify(list(Role.objects))

    def get(self, id):
        raise Exception("Not implemented yet!")
