from fastapi import Depends
from fastapi_blog.repositories.tag_repository import TagRepository, get_tag_repository


class TagService:
    def __init__(self, tag_repo: TagRepository):
        """
        Initializes the TagService with a repository for tag operations.

        Args:
            tag_repo: An instance of the TagRepository for tag-related operations.
        """
        self.tag_repo = tag_repo

    async def get_all(self):
        """
        Retrieves all tags from the database.

        Returns:
            list: A list of all Tag objects.
        """
        return await self.tag_repo.get_all()

def get_tag_service(tag_repo: TagRepository = Depends(get_tag_repository)):
    return TagService(tag_repo)