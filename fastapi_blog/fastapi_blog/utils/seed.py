import asyncio
from fastapi_blog.database import async_engine
from fastapi_blog.utils.seeds.blog_post_seed import seed_blogs
from fastapi_blog.utils.seeds.email_user_seed import seed_users
from fastapi_blog.utils.seeds.tag_seed import seed_tags
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

async def seed():
    Session = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)
    async with Session() as session:
        await seed_users(session)
        await seed_tags(session)
        await seed_blogs(session)

if __name__ == "__main__":
    asyncio.run(seed())