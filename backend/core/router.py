class DatabaseRouter:
    """
    A router to control all database operations on models in the
    different applications.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read api_v1 models go to default.
        All others go to nojo_django_db.
        """
        if model._meta.app_label == 'api_v1':
            return 'default'
        return 'nojo_django_db'

    def db_for_write(self, model, **hints):
        """
        Attempts to write api_v1 models go to default.
        All others go to nojo_django_db.
        """
        if model._meta.app_label == 'api_v1':
            return 'default'
        return 'nojo_django_db'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if models are in default and nojo_django_db.
        """
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Under SQLite mode, we allow api_v1 to migrate to default and others to nojo_django_db.
        Under MySQL mode, we completely disable migrations on default to avoid django_migrations table in nojo,
        and only run Django/metadata migrations (non-api_v1) on nojo_django_db.
        """
        import os
        force_sqlite = os.environ.get('FORCE_SQLITE') == 'True'

        if db == 'default':
            return force_sqlite and app_label == 'api_v1'
        elif db == 'nojo_django_db':
            return app_label != 'api_v1'
        return None
