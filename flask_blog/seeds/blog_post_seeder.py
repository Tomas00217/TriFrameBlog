from flask_seeder import Seeder, generator
from flask_blog.blogs.models import Tag, BlogPost
from flask_blog.accounts.models import EmailUser
from datetime import datetime, timedelta, timezone
from faker import Faker as PyFaker
import random


class BlogPostSeeder(Seeder):
    def __init__(self, db=None):
        super().__init__(db=db)
        self.priority = 3
        self.faker = PyFaker()

    def run(self):
        if BlogPost.query.count() != 0:
            print("Blog posts already exist, skipping seeding.")
            return

        sample_images = [
            '/media/food.jpg',
            '/media/tech.png',
            None
        ]

        users = EmailUser.query.all()
        tags = Tag.query.all()
        
        if not users or not tags:
            print("Error: Need users and tags before creating blog posts")
            return

        for i in range(10):
            title=self.faker.sentence(nb_words=6),
            content=self.faker.paragraph(nb_sentences=5),

            days_back = random.randint(0, 365)
            created_date = datetime.now(timezone.utc) - timedelta(days=days_back)

            post = BlogPost(
                title=title,
                content=content,
                image=random.choice(sample_images),
                created_at=created_date,
                author=random.choice(users)
            )

            post_tags = random.sample(tags, random.randint(2, min(5, len(tags))))
            post.tags.extend(post_tags)
            
            self.db.session.add(post)

        self.db.session.commit()
        print(f"Created blog posts")