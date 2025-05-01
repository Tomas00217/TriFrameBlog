from fastapi_blog.blogs.models import Tag
from sqlalchemy import select


async def seed_tags(session):
    tag_names = [
        'Technology', 'Programming', 'Python',
        'Travel', 'Food', 'Health', 'Science', 'Education',
        'Art', 'Music', 'Photography', 'Design', 'Books'
    ]

    result = await session.execute(select(Tag))
    if result.scalars().first():
        print("Tags already exist, skipping.")
        return

    tags = [Tag(name=name) for name in tag_names]
    session.add_all(tags)
    await session.commit()

    print("Created tags.")