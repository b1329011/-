import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
os.environ['FORCE_SQLITE'] = 'True'
django.setup()

from api_v1.models import User

email = 'air005831@gmail.com'
try:
    user = User.objects.get(email=email)
    print(f"User found: {user.email}")
    print(f"Role: {user.role}")
    print(f"Is active: {user.is_active}")
except User.DoesNotExist:
    print(f"User NOT found: {email}")
except Exception as e:
    print(f"Error: {e}")
