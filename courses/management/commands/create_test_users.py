from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create test users for load testing'

    def handle(self, *args, **options):
        users = [
            ('testuser', 'testpass123'),
            ('testuser2', 'testpass123'),
            ('testuser3', 'testpass123'),
        ]

        for username, password in users:
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(username, password=password)
                self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))
            else:
                self.stdout.write(self.style.WARNING(f'User {username} already exists'))
