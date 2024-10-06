from typing import Optional

from ninja import Schema, ModelSchema
from pydantic import Field

from apps.users.models import BlogUser


class BlogUserLoginSchema(Schema):
    username: str
    password: str


class BlogUserSchema(ModelSchema):
    username: str = Field(..., alias='user.username')

    class Meta:
        model = BlogUser
        fields = (
            'name',
        )


class BlogUserCreateSchema(Schema):
    name: Optional[str] = None
    username: str
    password: str
