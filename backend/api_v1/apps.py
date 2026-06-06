from django.apps import AppConfig


class ApiV1Config(AppConfig):
    name = 'api_v1'

    def ready(self):
        import os
        if os.environ.get('FORCE_SQLITE') == 'True':
            for model in self.get_models():
                model._meta.managed = True

        # Monkey-patch on_delete to DO_NOTHING for cross-database relations pointing to api_v1 models
        from django.apps import apps
        from django.db import models
        for model in apps.get_models():
            if model._meta.app_label != 'api_v1':
                for field in model._meta.local_fields:
                    if field.is_relation and field.related_model and field.related_model._meta.app_label == 'api_v1':
                        field.remote_field.on_delete = models.DO_NOTHING
