from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Create admin user with username:admin and password:password"

    def create_user(self):
        self.stdout.write(
            self.style.SUCCESS("Creating user:admin with password:12345678")
        )
        User.objects.create_superuser("admin", "admin@ai.co.tz", "12345678")

    def handle(self, *args, **options):
        try:
            user = User.objects.get(username="admin")
            self.stdout.write(self.style.SUCCESS("User exist. Deleting..."))
            user.delete()
            self.create_user()
        except User.DoesNotExist:
            self.create_user()
