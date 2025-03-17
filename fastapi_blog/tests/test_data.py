from fastapi_blog.blogs.models import BlogPost, Tag
from fastapi_blog.accounts.models import EmailUser
from tests.test_utils import TestingSessionLocal

TEST_USER = {
    "id": 1,
    "email": "test@example.com",
    "password": "securepassword",
    "is_active": True,
    "is_staff": False
}

async def create_test_users(session):
    """Create a test user for authentication tests."""
    user1 = EmailUser(
        id=TEST_USER["id"],
        email=TEST_USER["email"],
        is_active=TEST_USER["is_active"],
        is_staff=TEST_USER["is_staff"],
    )
    user1.set_password(TEST_USER["password"])

    user2 = EmailUser(
        id=2,
        email="test2@example.com",
        is_active=TEST_USER["is_active"],
        is_staff=TEST_USER["is_staff"],
    )
    user2.set_password(TEST_USER["password"])

    session.add_all([user1, user2])
    await session.commit()
    return user1, user2


async def create_test_tags(session):
    """Create test tags for blog filtering tests."""
    tag1 = Tag(name="Food", slug="food")
    tag2 = Tag(name="Tech", slug="tech")
    
    session.add_all([tag1, tag2])
    await session.commit()
    
    await session.refresh(tag1)
    await session.refresh(tag2)
    
    return tag1, tag2


async def create_test_blogs(session, user_id, user2_id, tags):
    """Create test blog posts."""
    tag1, tag2 = tags

    blog1 = BlogPost(
        title="Blog1 search",
        content="Content1",
        author_id=user_id,
        tags=[tag1]
    )
    blog2 = BlogPost(
        title="Blog2",
        content="Content2",
        author_id=user_id,
        tags=[tag2]
    )
    
    blog3 = BlogPost(
        title="Blog3",
        content="Content3",
        author_id=user2_id,
        tags=[tag1]
    )

    blog4 = BlogPost(
        title="Blog4 search",
        content="Content4",
        author_id=user_id,
        tags=[tag1]
    )

    blog5 = BlogPost(
        title="Blog5",
        content="Content5",
        author_id=user_id,
        tags=[tag1]
    )

    blog6 = BlogPost(
        title="Blog6",
        content="Content6",
        author_id=user_id,
        tags=[tag1]
    )
    
    blog7 = BlogPost(
        title="Blog7",
        content="Content7",
        author_id=user_id,
        tags=[tag1, tag2]
    )

    session.add_all([blog1, blog2, blog3, blog4, blog5, blog6, blog7])
    await session.commit()
    
    await session.refresh(blog1)
    await session.refresh(blog2)
    await session.refresh(blog3)
    await session.refresh(blog4)
    await session.refresh(blog5)
    await session.refresh(blog6)
    await session.refresh(blog7)

    return blog1, blog2, blog3, blog4, blog5, blog6, blog7

async def seed_test_data():
    """Seed the test database with test data."""
    async with TestingSessionLocal() as session:
        users = await create_test_users(session)
        tags = await create_test_tags(session)
        blogs = await create_test_blogs(session, users[0].id, users[1].id, tags)