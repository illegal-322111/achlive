from decimal import Decimal
from django.core.management.base import BaseCommand
from store.models import Product

class Command(BaseCommand):
    help = 'Set product balances to 2 decimal places'

    def handle(self, *args, **options):
        # Get all products
        all_products = Product.objects.all()

        # Iterate through products
        for product in all_products:
            # Check if the balance has more than 2 decimal places
            balance_str = product.Balance.replace(',', '')  # Remove commas if present
            if '.' in balance_str:
                integer_part, decimal_part = balance_str.split('.')
                if len(decimal_part) > 2:
                    # Convert the balance to a Decimal and round to 2 decimal places
                    new_balance = Decimal(balance_str).quantize(Decimal('0.00'))

                    # Update the product's balance
                    product.Balance = str(new_balance)
                    product.save()

        self.stdout.write(self.style.SUCCESS('Product balances updated to 2 decimal places successfully.'))
