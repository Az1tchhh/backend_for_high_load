from datetime import datetime
from typing import Optional, List

from ninja import ModelSchema, Schema
from pydantic import Field

from apps.blogs.models import Post, Comment, Tag


class TagSchema(ModelSchema):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
        )


class TagCreateSchema(ModelSchema):
    class Meta:
        model = Tag
        fields = (
            'name',
        )


class PostSchema(ModelSchema):
    author: str = Field(..., alias='author.username')

    class Meta:
        model = Post
        fields = (
            'id',
            'title',
            'content',
            'tags',
            'created_at',
            'updated_at',
        )


class PostCreateSchema(ModelSchema):
    tags: List[int] = []

    class Meta:
        model = Post
        fields = (
            'title',
            'content',
            'tags'
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


class CommentSchema(ModelSchema):
    author_name: str = Field(..., alias='author.username')
    post_title: str = Field(..., alias='post.title')

    class Meta:
        model = Comment
        fields = (
            'id',
            'text',
            'author',
            'post',
            'created_at',
            'updated_at',
        )


class CommentSimpleSchema(Schema):
    id: int
    author_name: str = Field(..., alias='author.username')
    author_id: int
    text: str
    created_at: datetime
    updated_at: datetime


class CommentCreateSchema(Schema):
    text: str
    post_id: int = Field(..., alias='post_id')
