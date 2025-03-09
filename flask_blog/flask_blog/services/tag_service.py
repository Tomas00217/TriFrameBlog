from flask import abort
from flask_blog.repositories.tag_repository import TagRepository

class TagService:
    def __init__(self, tag_repo: TagRepository):
        """
        Initializes the TagService with a repository for tag operations.

        Args:
            tag_repo (TagRepository): An instance of the TagRepository for tag-related operations.
        """
        self.tag_repo = tag_repo

    def get_all(self):
        """
        Retrieves all tags from the database.

        Returns:
            list: A list of all Tag objects.
        """
        return self.tag_repo.get_all()