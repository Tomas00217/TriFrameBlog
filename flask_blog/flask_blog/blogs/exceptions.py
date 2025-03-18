class BlogPostNotFoundError(Exception):
    """Custom exception for blog not found"""
    def __init__(self):
        super().__init__("Blog post not found")