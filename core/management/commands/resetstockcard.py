from django.core.management.base import BaseCommand, CommandError
from core.models import StockCard, StockOnHand


class Command(BaseCommand):
    help = "Reset stock cards and stock on hand to zero"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("Deleting all records in stock cards")
        )
        StockOnHand.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS("Deleting all records in stock on hand")
        )
        StockOnHand.objects.all().delete()
