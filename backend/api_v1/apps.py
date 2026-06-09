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

        # Start a background thread to check match statuses periodically
        import sys
        is_runserver = 'runserver' in sys.argv or any('run_dev_server.py' in arg for arg in sys.argv)
        if is_runserver:
            has_noreload = '--noreload' in sys.argv or any('run_dev_server.py' in arg for arg in sys.argv)
            is_reloader = not has_noreload and os.environ.get('RUN_MAIN') != 'true'
            if not is_reloader:
                import threading
                import time
                
                def check_matches_loop():
                    time.sleep(5)  # Wait for Django to finish initializing
                    while True:
                        try:
                            from api_v1.views import update_all_match_statuses
                            from django.db import connections
                            print("[Background Task] Checking match statuses...", flush=True)
                            update_all_match_statuses()
                            connections.close_all()
                        except Exception as e:
                            print(f"Background thread match status update failed: {e}", flush=True)
                        time.sleep(30)  # Run every 30 seconds
                
                t = threading.Thread(target=check_matches_loop, name="MatchStatusChecker", daemon=True)
                t.start()
