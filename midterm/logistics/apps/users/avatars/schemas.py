from typing import Optional

from ninja import Schema, ModelSchema, UploadedFile, File
from pydantic import Field

from apps.users.avatars.models import Avatar


class AvatarSchema(ModelSchema):
    class Meta:
        model = Avatar
        fields = (
            'id',
            'name',
            'image',
        )


class AvatarCreateSchema(Schema):
    name: str


class AvatarUpdateSchema(Schema):
    name: Optional[str] = None
