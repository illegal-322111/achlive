import csv
from account.models import Customer
from django.core.management.base import BaseCommand
from passlib.hash import pbkdf2_sha256

class Command(BaseCommand):
    help = 'Import users from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the input CSV file')

    def handle(self, *args, **options):
        file_path = options['file_path']

        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                username = row['username']
                email = row['email']
                password = row['password']
                is_active = row['is_active']
                verified = row['verified']
                is_staff = row['is_staff']
                # If you hashed the passwords during export, you need to rehash them before saving
                

                # Create or update the user in the database
                user, created = Customer.objects.get_or_create(user_name=username, defaults={'email': email})
                user.email = email
                user.is_active = is_active
                user.verified = verified
                user.is_staff = is_staff
                user.password= password
                user.save()

        self.stdout.write(self.style.SUCCESS("User import complete."))
