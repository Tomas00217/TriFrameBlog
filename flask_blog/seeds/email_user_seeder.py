from flask_seeder import Seeder, Faker, generator
from flask_blog.accounts.models import EmailUser

class EmailUserSeeder(Seeder):
    def __init__(self, db=None):
        super().__init__(db=db)
        self.priority = 1

    def run(self):
        if EmailUser.query.count() > 1:
            print("Users already exist, skipping seeding.")
            return

        faker = Faker(
            cls=EmailUser,
            init={
                "email": generator.Email(),
                "password": "Password123"
            }
        )

        for _ in range(5):
            user = faker.create()[0]

            existing_user = EmailUser.query.filter_by(email=user.email).first()
            if existing_user:
                continue

            self.db.session.add(user)

        self.db.session.commit()
        print(f"Created regular users")