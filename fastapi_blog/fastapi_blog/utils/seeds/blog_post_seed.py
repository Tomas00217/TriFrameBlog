from datetime import datetime, timedelta, timezone
import random
from faker import Faker
from fastapi_blog.accounts.models import EmailUser
from fastapi_blog.blogs.models import BlogPost, Tag
from sqlalchemy import select


async def seed_blogs(session, count: int = 10):
    faker = Faker()

    posts_result = await session.execute(select(BlogPost))
    if posts_result.scalars().first():
        print("Blog posts already exist, skipping.")
        return

    sample_images = [
        '/media/food.jpg',
        '/media/tech.png',
        None
    ]

    users_result = await session.execute(select(EmailUser))
    users = users_result.scalars().all()

    tags_result = await session.execute(select(Tag))
    tags = tags_result.scalars().all()

    if not users or not tags:
        print("You need users and tags first.")
        return

    posts = []
    for _ in range(count):
        post = BlogPost(
            title=faker.sentence(),
            content=faker.paragraph(nb_sentences=5),
            image=random.choice(sample_images),
            created_at=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=random.randint(0, 365)),
            author_id=random.choice(users).id
        )
        post.tags.extend(random.sample(tags, random.randint(2, min(5, len(tags)))))
        posts.append(post)

    session.add_all(posts)
    await session.commit()

    print("Created blog posts.")