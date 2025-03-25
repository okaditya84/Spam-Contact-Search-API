import random
import string
from django.core.management.base import BaseCommand
from api.models import CustomUser, Contact, SpamReport

def random_phone():
    return ''.join(random.choices(string.digits, k=10))

def random_name():
    first_names = ['John', 'Jane', 'Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank']
    last_names = ['Smith', 'Doe', 'Johnson', 'Williams', 'Brown', 'Jones']
    return f"{random.choice(first_names)} {random.choice(last_names)}"

class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def handle(self, *args, **options):
        # Clear existing data
        CustomUser.objects.all().delete()
        Contact.objects.all().delete()
        SpamReport.objects.all().delete()

        users = []
        # Create 20 users
        for _ in range(20):
            phone = random_phone()
            while CustomUser.objects.filter(phone_number=phone).exists():
                phone = random_phone()
            user = CustomUser.objects.create_user(
                phone_number=phone,
                name=random_name(),
                password='password123',
                email=f"{phone}@example.com"
            )
            users.append(user)
            self.stdout.write(f"Created user {user}")

        # For each user, create 5 contacts
        for user in users:
            for _ in range(5):
                contact_phone = random_phone()
                contact_name = random_name()
                Contact.objects.create(owner=user, phone_number=contact_phone, name=contact_name)
            self.stdout.write(f"Created contacts for user {user.phone_number}")

        # Randomly mark 10 numbers as spam by random users
        all_numbers = []
        for user in users:
            all_numbers.append(user.phone_number)
            contacts = Contact.objects.filter(owner=user)
            for contact in contacts:
                all_numbers.append(contact.phone_number)
        for _ in range(10):
            phone = random.choice(all_numbers)
            reporter = random.choice(users)
            try:
                SpamReport.objects.create(phone_number=phone, reported_by=reporter)
                self.stdout.write(f"User {reporter.phone_number} reported {phone} as spam")
            except Exception:
                continue

        self.stdout.write(self.style.SUCCESS('Sample data population complete.'))
