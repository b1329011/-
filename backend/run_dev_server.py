import os
import sys

# Force SQLite mode
os.environ.setdefault('FORCE_SQLITE', 'False')
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

from django.core.management import execute_from_command_line
if __name__ == '__main__':
    execute_from_command_line([sys.argv[0], 'runserver', '8088', '--noreload'])
