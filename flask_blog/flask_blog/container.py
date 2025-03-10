from flask_blog.repositories.blog_post_repository import BlogPostRepository
from flask_blog.repositories.email_user_repository import EmailUserRepository
from flask_blog.repositories.tag_repository import TagRepository
from shared.services.blog_post_service import BlogPostService
from shared.services.email_user_service import EmailUserService
from shared.services.tag_service import TagService


class Container:
    def __init__(self):
        self.blog_post_repo = BlogPostRepository()
        self.tag_repo = TagRepository()
        self.user_repo = EmailUserRepository()
        
        self.blog_service = BlogPostService(self.blog_post_repo, self.tag_repo)
        self.tag_service = TagService(self.tag_repo)
        self.user_service = EmailUserService(self.user_repo)

container = Container()