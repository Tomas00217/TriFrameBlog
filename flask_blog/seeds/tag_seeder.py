from flask_blog.blogs.models import Tag
from flask_seeder import Seeder

class TagSeeder(Seeder):
    def __init__(self, db=None):
        super().__init__(db=db)
        self.priority = 2

    def run(self):
        if Tag.query.count() != 0:
            print("Tags already exist, skipping seeding.")
            return

        tag_names = [
            'Technology', 'Programming', 'Python', 
            'Travel', 'Food', 'Health', 'Science', 'Education',
            'Art', 'Music', 'Photography', 'Design', 'Books',
        ]

        for name in tag_names:
            existing_tag = Tag.query.filter_by(name=name).first()
            if existing_tag:
                continue
                
            tag = Tag(name=name)
            self.db.session.add(tag)

        self.db.session.commit()
        print(f"Created tags")