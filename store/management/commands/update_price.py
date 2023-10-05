import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from payment.models import Balance

class Command(BaseCommand):
    help = 'Randomly update balances and prices'

    def handle(self, *args, **options):
        # Define pr
        balances = Balance.objects.all()
        for balance in balances:
            if balance.balance is None:
                balance.balance = 0
                balance.save()
            else:
                pass

        self.stdout.write(self.style.SUCCESS('Balances updated successfully.'))
