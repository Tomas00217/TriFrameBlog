from flask_blog.extensions import db
from flask_blog.blogs.models import BlogPost, Tag
from sqlalchemy import func, select, update

class BlogPostRepository:
    def get_all_query(self, tag_slugs=None, search=None):
        """
        Constructs a query to retrieve blog posts, optionally filtered by tags or search terms.

        Args:
            tag_slugs (list, optional): A list of tag slugs to filter the blogs by tags. Defaults to None.
            search (str, optional): A search string to filter blogs by title. Defaults to None.

        Returns:
           The select statement to retrieve blogs by the specified author.
        """
        stmt = select(BlogPost).join(BlogPost.tags)

        if tag_slugs:
            for tag_slug in tag_slugs:
                stmt = stmt.filter(BlogPost.tags.any(Tag.slug == tag_slug))

        if search:
            stmt = stmt.filter(BlogPost.title.ilike(f"%{search}%"))

        stmt = stmt.order_by(BlogPost.created_at.desc()).distinct()
        return stmt
    
    def get_all(self, tag_slugs=None, search=None):
        """
        Executes the constructed query to retrieve all blog posts, optionally filtered by tags or search terms.

        Args:
            tag_slugs (list, optional): A list of tag slugs to filter the blogs by tags. Defaults to None.
            search (str, optional): A search string to filter blogs by title. Defaults to None.

        Returns:
            list: A list of BlogPost objects matching the query criteria.
        """
        stmt = self.get_all_query(tag_slugs, search)

        return db.session.execute(stmt).scalars()

    def get_paginated(self, stmt, page=1, per_page=6):
        """
        Paginates a given query statement.

        Args:
            stmt: The SQLAlchemy select statement to paginate.
            page (int, optional): The page number for pagination. Defaults to 1.
            per_page (int, optional): The number of items per page. Defaults to 6.

        Returns:
            Pagination: A Paginated result containing a subset of query results based on the page and per_page values.
        """
        return db.paginate(stmt, page=page, per_page=per_page)

    def get_by_id(self, blog_id):
        """
        Retrieves a blog post by its unique identifier (ID).

        Args:
            blog_id (int): The ID of the blog post.

        Returns:
            BlogPost or None: The BlogPost object if found, or None if no blog with the specified ID exists.
        """
        stmt = select(BlogPost).where(BlogPost.id == blog_id)

        return db.session.execute(stmt).scalar_one_or_none()

    def get_by_author_query(self, user):
        """
        Constructs a query to retrieve all blog posts authored by a specific user.

        Args:
            user (User): The user whose blogs are to be retrieved.

        Returns:
            The select statement to retrieve blogs by the specified author.
        """
        return select(BlogPost).filter(BlogPost.author_id == user.id)

    def get_by_author(self, user):
        """
        Executes a query to retrieve all blog posts authored by a specific user.

        Args:
            user (EmailUser): The user whose blogs are to be retrieved.

        Returns:
            list: A list of BlogPost objects authored by the specified user.
        """
        stmt = self.get_by_author_query(user)

        return db.session.execute(stmt).scalars()
    
    def get_recent(self, limit=3):
        """
        Retrieves the most recent blog posts, ordered by creation date.

        Args:
            limit (int, optional): The maximum number of recent blog posts to return. Defaults to 3.

        Returns:
            list: A list of the most recent BlogPost objects.
        """
        stmt = select(BlogPost).order_by(BlogPost.created_at.desc()).limit(limit)

        return db.session.execute(stmt).scalars().all()

    def get_related(self, blog, limit=3):
        """
        Retrieves related blog posts based on shared tags, excluding the current blog post.

        Args:
            blog (BlogPost): The blog post to find related posts for.
            limit (int, optional): The maximum number of related blog posts to return. Defaults to 3.

        Returns:
            list: A list of BlogPost objects related to the specified blog post.
        """
        stmt = (
            select(BlogPost)
            .join(BlogPost.tags)
            .filter(Tag.id.in_([tag.id for tag in blog.tags]))
            .filter(BlogPost.id != blog.id)
            .group_by(BlogPost.id)
            .order_by(BlogPost.id, func.random())
            .limit(limit)
        )

        return db.session.execute(stmt).scalars().all()

    def create(self, title, content, image, author, tags):
        """
        Creates and persists a new blog post in the database.

        Args:
            title (str): The title of the new blog post.
            content (str): The content/body of the new blog post.
            image (str): The URL or file path to the image associated with the new blog post.
            author (EmailUser): The author of the new blog post.
            tags (list): A list of Tag objects to associate with the new blog post.

        Returns:
            BlogPost: The created BlogPost object.
        """
        blog_post = BlogPost(title=title, content=content, image=image, author=author)
        db.session.add(blog_post)
        db.session.flush()
        blog_post.tags.extend(tags)
        db.session.commit()

        return blog_post

    def update(self, blog, title, content, image, tags):
        """
        Updates an existing blog post with new data.

        Args:
            blog (BlogPost): The blog post to update.
            title (str): The new title for the blog post.
            content (str): The new content for the blog post.
            image (str): The new image URL or file path for the blog post.
            tags (list): A list of new Tag objects to associate with the blog post.

        Returns:
            BlogPost: The updated BlogPost object.
        """
        stmt = (
            update(BlogPost)
            .where(BlogPost.id == blog.id)
            .values(title=title, content=content, image=image)
        )
        db.session.execute(stmt)
        blog.tags = tags
        db.session.commit()

        return blog

    def delete(self, blog):
        """
        Deletes a blog post from the database.

        Args:
            blog (BlogPost): The blog post to delete.

        Returns:
            None
        """
        db.session.delete(blog)
        db.session.commit()