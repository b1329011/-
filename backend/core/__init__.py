from django.db.models import ForeignKey
from django.db.models.query import QuerySet

# --- Patch 1: Stop ForeignKey from creating physical db constraints pointing to User ---
_original_fk_init = ForeignKey.__init__

def _patched_fk_init(self, *args, **kwargs):
    to = kwargs.get('to') or (args[0] if args else None)
    if to:
        from django.conf import settings
        user_model_str = getattr(settings, 'AUTH_USER_MODEL', 'api_v1.User')
        
        is_user = False
        if isinstance(to, str):
            to_lower = to.lower()
            if to_lower in ('api_v1.user', 'user', user_model_str.lower()):
                is_user = True
        elif hasattr(to, '_meta') and to._meta.label_lower == 'api_v1.user':
            is_user = True
            
        if is_user:
            kwargs['db_constraint'] = False
            
    _original_fk_init(self, *args, **kwargs)

ForeignKey.__init__ = _patched_fk_init


# --- Patch 2: Stop cross-database select_related('user') on Token and LogEntry ---
_original_select_related = QuerySet.select_related

def _patched_select_related(self, *fields):
    if not fields:
        return _original_select_related(self)
        
    cleaned_fields = []
    for field in fields:
        if field == 'user' and self.model._meta.label_lower in ('admin.logentry', 'authtoken.token'):
            continue
        cleaned_fields.append(field)
        
    if not cleaned_fields:
        # Passing None clears select_related in Django
        return _original_select_related(self, None)
        
    return _original_select_related(self, *cleaned_fields)

QuerySet.select_related = _patched_select_related


# --- Patch 3: Disable django_migrations recorder on default database in MySQL mode ---
import os
try:
    from django.db.migrations.recorder import MigrationRecorder

    _original_ensure_schema = MigrationRecorder.ensure_schema
    _original_applied_migrations = MigrationRecorder.applied_migrations
    _original_record_applied = MigrationRecorder.record_applied
    _original_record_unapplied = MigrationRecorder.record_unapplied

    def _patched_ensure_schema(self):
        if self.connection.alias == 'default' and os.environ.get('FORCE_SQLITE') != 'True':
            return
        _original_ensure_schema(self)

    def _patched_applied_migrations(self):
        if self.connection.alias == 'default' and os.environ.get('FORCE_SQLITE') != 'True':
            return {}
        return _original_applied_migrations(self)

    def _patched_record_applied(self, app, name):
        if self.connection.alias == 'default' and os.environ.get('FORCE_SQLITE') != 'True':
            return
        _original_record_applied(self, app, name)

    def _patched_record_unapplied(self, app, name):
        if self.connection.alias == 'default' and os.environ.get('FORCE_SQLITE') != 'True':
            return
        _original_record_unapplied(self, app, name)

    MigrationRecorder.ensure_schema = _patched_ensure_schema
    MigrationRecorder.applied_migrations = _patched_applied_migrations
    MigrationRecorder.record_applied = _patched_record_applied
    MigrationRecorder.record_unapplied = _patched_record_unapplied
except ImportError:
    pass
