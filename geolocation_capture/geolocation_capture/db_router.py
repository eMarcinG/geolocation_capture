from django.db import connections
from django.db.utils import OperationalError

class PrimaryReplicaRouter:
    def db_for_read(self, model, **hints):
        try:
            connections['default'].ensure_connection()
            return 'default'
        except OperationalError:
            return 'replica'  

    def db_for_write(self, model, **hints):
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db == 'default'