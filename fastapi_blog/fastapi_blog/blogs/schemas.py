from pydantic import BaseModel, Field
from typing import List, Optional

class PaginatedResponse[T](BaseModel):
    data: List[T]
    total: int
    page: int
    per_page: int
    total_pages: int
    next_page: Optional[int]
    prev_page: Optional[int]

class BlogQueryParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number for pagination")
    per_page: int = Field(default=6, ge=1, description="Number of items per page")
    search: Optional[str] = Field(None, description="Search query for blog posts")
    tag: Optional[str] = Field(None, description="Comma-separated list of tag slugs")
