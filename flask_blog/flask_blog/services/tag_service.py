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

    def get_by_id(self, tag_id):
        """
        Retrieves a tag by its unique identifier (ID).

        Args:
            tag_id (int): The ID of the tag to retrieve.

        Raises:
            abort(404): If no tag is found with the provided ID.

        Returns:
            Tag: The Tag object corresponding to the provided ID.
        """
        tag = self.tag_repo.get_by_id(tag_id)
        if not tag:
            abort(404, description="Tag not found")

        return tag

    def get_by_ids(self, tag_ids):
        """
        Retrieves multiple tags by their unique identifiers (IDs).

        Args:
            tag_ids (list): A list of tag IDs to retrieve.

        Returns:
            list: A list of Tag objects corresponding to the specified IDs.
        """
        return self.tag_repo.get_by_ids(tag_ids)