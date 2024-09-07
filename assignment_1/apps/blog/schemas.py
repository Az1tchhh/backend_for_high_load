from typing import Optional

from ninja import ModelSchema, Schema
from pydantic import Field

from apps.blog.models import Post


class PostSchema(ModelSchema):
    author: str = Field(..., alias='author.username')

    class Meta:
        model = Post
        fields = (
            'id',
            'title',
            'content',
            'created_at',
            'updated_at',
        )


class PostCreateSchema(ModelSchema):
    class Meta:
        model = Post
        fields = (
            'title',
            'content',
        )


class PostUpdateSchema(Schema):
    title: Optional[str] = None
    content: Optional[str] = None


class PostRetrieveSchema(ModelSchema):
    author: str = Field(..., alias='author.username')
    author_name: str = Field(..., alias='author.blog_user.name')

    class Meta:
        model = Post
        fields = (
            'id',
            'title',
            'content',
            'author',
            'created_at',
            'updated_at',
        )
