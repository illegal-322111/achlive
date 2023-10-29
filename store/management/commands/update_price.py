from django.core.management.base import BaseCommand
from store.models import Product

class Command(BaseCommand):
    help = 'Randomly update balances and prices'

    def handle(self, *args, **options):
        
        # Filter products based on the Balance field
        filtered_products = Product.objects.filter(price=350)

        # Update the selected products with the new balance
        for product in filtered_products:
            product.Balance = str(float(product.Balance) * 10)
            product.save()

        self.stdout.write(self.style.SUCCESS('Balances updated successfully.'))
