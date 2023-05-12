# myapp/management/commands/import_products.py

from django.core.management.base import BaseCommand
from store.models import *
import csv
from django.core.files import File
class Command(BaseCommand):
    help = 'Import products from a data file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the data file')

    

    def handle(self, *args, **options):
        file_path = options['file_path']

        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                pdf_path = row['pdf']
                if pdf_path:
                    with open(pdf_path, 'rb') as pdf_file:
                        pdf = File(pdf_file)
                        product_data = {
                            'name': row['name'],
                            'category': Category.objects.get(name=row['category']),
                            'Balance': row['Balance'],
                            'Title': row['Title'],
                            'Info': row['Info'],
                            'slug': row['slug'],
                            'price': float(row['price']),
                            'pdf': pdf,
                        }
                        Product.objects.create(**product_data)

        self.stdout.write(self.style.SUCCESS('Products imported successfully.'))


