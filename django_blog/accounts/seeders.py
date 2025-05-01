from accounts.models import EmailUser
from django_seeding import seeders
from django_seeding.seeder_registry import SeederRegistry
from faker import Faker

@SeederRegistry.register
class EmailUserSeeder(seeders.Seeder):
    id = 'EmailUserSeeder'
    priority = 1

    def seed(self):
        faker = Faker()

        if EmailUser.objects.count() > 1:
            print("Users already exist, skipping.")
            return

        for _ in range(5):
            EmailUser.objects.create(
                email=faker.email(),
                password='Password123'
            )

        print("Created users.")