import bcrypt
from faker import Faker
from fastapi_blog.accounts.models import EmailUser
from sqlalchemy import select


async def seed_users(session, count: int = 5):
    faker = Faker()

    result = await session.execute(select(EmailUser))
    if len(result.scalars().all()) > 1:
        print("Users already exist, skipping.")
        return

    users = []
    for _ in range(count):
        user = EmailUser(
            email=faker.unique.email(),
            is_active=True
        )
        user.set_password("Password123")
        users.append(user)

    session.add_all(users)
    await session.commit()

    print("Created users.")