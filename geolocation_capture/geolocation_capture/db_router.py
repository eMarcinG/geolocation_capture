from django.conf import settings
from django.db.utils import OperationalError
import dj_database_url

class FailoverRouter:
    """
    A router to control all database operations for reading and writing.
    In case of an error with the primary database, it switches to the replica.
    """

    def db_for_read(self, model, **hints):
        """
        Attempts to read from the primary database.
        If it fails, read from the replica.
        """
        try:
            settings.DATABASES['default'] = dj_database_url.config(default=os.getenv('PRIMARY_DB_URL'))
            return 'default'
        except OperationalError:
            print("Primary database is down, switching to replica")
            settings.DATABASES['default'] = dj_database_url.config(default=os.getenv('REPLICA_DB_URL'))
            return 'default'

    def db_for_write(self, model, **hints):
        """
        Attempts to write to the primary database.
        If it fails, write to the replica.
        """
        try:
            settings.DATABASES['default'] = dj_database_url.config(default=os.getenv('PRIMARY_DB_URL'))
            return 'default'
        except OperationalError:
            print("Primary database is down, switching to replica")
            settings.DATABASES['default'] = dj_database_url.config(default=os.getenv('REPLICA_DB_URL'))
            return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow any relation if both models are in the same database.
        """
        db_obj1 = hints.get('instance', obj1)._state.db
        db_obj2 = hints.get('instance', obj2)._state.db
        if db_obj1 and db_obj2:
            if db_obj1 == db_obj2:
                return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Ensure that all migrations are applied to the primary database.
        """
        return db == 'default'
