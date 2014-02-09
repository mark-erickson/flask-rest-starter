from flask.ext.security import UserMixin, RoleMixin
from mongoengine import BooleanField
from mongoengine import DateTimeField
from mongoengine import Document
from mongoengine import ListField
from mongoengine import ReferenceField
from mongoengine import StringField

class Role(Document, RoleMixin):
    _json = ('id', 'name', 'description')

    name = StringField(max_length=80, unique=True)
    description = StringField(max_length=255)

    def export(self):
        d = {}
        for p in self._json:
            d[p] = self[p]
        return d

class User(Document, UserMixin):
    email = StringField(max_length=255)
    password = StringField(max_length=255)
    active = BooleanField(default=True)
    confirmed_at = DateTimeField()
    roles = ListField(ReferenceField(Role), default=[])
