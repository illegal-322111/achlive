from django.core.management.base import BaseCommand
from store.models import Product, Category
import csv

class Command(BaseCommand):
    help = 'Update products from a data file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the data file')

    def handle(self, *args, **options):
        file_path = options['file_path']

        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                category_name = row['Category']
                category, _ = Category.objects.get_or_create(name=category_name)

                product_data = {
                    'name': row['Name'],
                    'category': category,
                    'Balance': row['Balance'],
                    'Title': row['Title'],
                    'Info': row['Info'],
                    'price': float(row['Price']),
                }

                try:
                    product = Product.objects.get(slug=row['Slug'], category=category)
                    for key, value in product_data.items():
                        setattr(product, key, value)

                    pdf_path = row['PDF']
                    if pdf_path:
                        with open(pdf_path, 'rb') as pdf_file:
                            product.pdf.save(pdf_path, pdf_file, save=True)
                    else:
                        product.pdf = None

                    product.save()
                except Product.DoesNotExist:
                    Product.objects.create(**product_data)

        self.stdout.write(self.style.SUCCESS('Products updated successfully.'))
