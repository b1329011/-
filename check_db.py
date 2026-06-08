import os
import django
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api_v1.models import Sport, GameMatch, User, MatchParticipant

print(f"Users: {User.objects.count()}")
print(f"Sports: {Sport.objects.count()}")
for s in Sport.objects.all():
    print(f"  - {s.name} ({s.chinese_name})")
print(f"Matches: {GameMatch.objects.count()}")
print(f"Participants: {MatchParticipant.objects.count()}")
