import random
from accounts.models import EmailUser
from blogs.models import BlogPost, Tag
from django_seeding import seeders
from django_seeding.seeder_registry import SeederRegistry
from django.utils.timezone import now, timedelta
from faker import Faker

@SeederRegistry.register
class TagSeeder(seeders.EmptySeeder):
    id = 'TagSeeder'
    priority = 2

    def seed(self):
        if Tag.objects.exists():
            print("Tags already exist, skipping.")
            return

        tag_names = [
            'Technology', 'Programming', 'Python',
            'Travel', 'Food', 'Health', 'Science', 'Education',
            'Art', 'Music', 'Photography', 'Design', 'Books',
        ]
        for name in tag_names:
            Tag.objects.create(name=name)

        print("Created tags.")

@SeederRegistry.register
class BlogPostSeeder(seeders.Seeder):
    id = 'BlogPostSeeder'
    priority = 3

    def seed(self):
        faker = Faker()

        if BlogPost.objects.exists():
            print("Blog posts already exist, skipping.")
            return

        users = list(EmailUser.objects.all())
        tags  = list(Tag.objects.all())
        sample_images = ['/images/food.jpg', '/images/tech.png', None]

        for _ in range(10):
            created_date = now() - timedelta(days=random.randint(0, 365))
            post = BlogPost.objects.create(
                title   = faker.sentence(nb_words=6),
                content = faker.paragraph(nb_sentences=5),
                image   = random.choice(sample_images),
                created_at = created_date,
                author  = random.choice(users),
            )
            post.tags.add(*random.sample(tags, random.randint(2, min(5, len(tags)))))

        print("Created blog posts.")