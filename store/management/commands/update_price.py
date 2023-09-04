from django.core.management.base import BaseCommand
from store.models import Product, Category

class Command(BaseCommand):
    help = 'Update products based on balance'

    def handle(self, *args, **options):
        # Define price ranges and their corresponding prices
        price_ranges = [
            ('7000', '7999', 200),
            ('8000', '8999', 250),
            ('9000', '9999', 300),
            ('10000', '20000', 350),
        ]

        # Loop through price ranges
        for start_str, end_str, price in price_ranges:
            products_to_update = Product.objects.filter(Balance__gte=start_str, Balance__lte=end_str)

            for product in products_to_update:
                product.price = price
                product.save()

        self.stdout.write(self.style.SUCCESS('Products updated successfully.'))
