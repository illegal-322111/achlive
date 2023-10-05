import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from store.models import Product

class Command(BaseCommand):
    help = 'Randomly update product balances and prices'

    def handle(self, *args, **options):
        # Define price ranges and their corresponding prices
        price_ranges = [
            (7000, 7999, Decimal('200.00')),
            (6000, 6999, Decimal('150.00')),
            (8000, 8999, Decimal('250.00')),
            (9000, 9999, Decimal('300.00')),
            (10000, 10100, Decimal('350.00')),
        ]

        # Get all products in the database
        all_products = Product.objects.all()

        # Calculate the number of products to update in each group (1/4 of the total)
        num_products = len(all_products)
        num_to_update = int(num_products / 5)  # Divide into 4 equal groups

        # Shuffle the products randomly
        shuffled_products = random.sample(list(all_products), num_products)

        # Update the selected products with the new price and balance
        for i, product in enumerate(shuffled_products):
            # Determine the price range based on the current group
            price_index = i % len(price_ranges)
            start, end, price = price_ranges[price_index]

            # Convert Balance to a float, apply changes, and round to 2 decimal places
            current_balance = Decimal(product.Balance.replace(',', ''))  # Remove commas if present
            new_balance = round(random.randint(start, end), 2)  # Decrease by 10% and round to 2 decimal places

            # Update price and balance
            product.price = price + round(random.randint(1, 50), 2)
            product.Balance = str(new_balance)  # Convert back to string for CharField
            product.save()

        self.stdout.write(self.style.SUCCESS('Products updated successfully.'))
