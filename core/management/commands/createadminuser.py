from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()
DEFAULT_USERNAME = 'admin'
DEFAULT_PASSWORD = '12345678'
DEFAULT_EMAIL = 'admin@admin.com'


class Command(BaseCommand):
    help = f"Create admin user with username:{DEFAULT_USERNAME} and password:{DEFAULT_PASSWORD}"

    def create_user(self):
        self.stdout.write(
            self.style.SUCCESS(f"Creating user:{DEFAULT_USERNAME} with password:{DEFAULT_PASSWORD}")
        )
        User.objects.create_superuser(DEFAULT_USERNAME, DEFAULT_EMAIL, DEFAULT_PASSWORD)

    def handle(self, *args, **options):
        try:
            user = User.objects.get(username="admin")
            self.stdout.write(self.style.SUCCESS("User exist. Deleting..."))
            user.delete()
            self.create_user()
        except User.DoesNotExist:
            self.create_user()
