from django.core.management.base import BaseCommand
from api_v1.views import update_all_match_statuses

class Command(BaseCommand):
    help = 'Updates the statuses of all active game matches based on start/end times and sends notifications.'

    def handle(self, *args, **options):
        self.stdout.write("Updating game matches...")
        update_all_match_statuses()
        self.stdout.write(self.style.SUCCESS("Successfully updated game matches!"))
