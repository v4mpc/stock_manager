from core.models import Unit
from django.core.management.base import BaseCommand, CommandError

DEFAULT_UNIT_NAME = "Kilogram"
DEFAULT_UNIT_CODE = "KG"


class Command(BaseCommand):
    help = "Create Unit of measure."

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(f"Creating unit name:{DEFAULT_UNIT_NAME} with code:{DEFAULT_UNIT_CODE}")
        )
        obj, created = Unit.objects.get_or_create(name=DEFAULT_UNIT_NAME, code=DEFAULT_UNIT_CODE,
                                                  defaults={"code": DEFAULT_UNIT_CODE})
