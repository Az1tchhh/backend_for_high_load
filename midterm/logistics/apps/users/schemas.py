from datetime import date
from typing import Optional

from ninja import Schema, ModelSchema
from pydantic import EmailStr, Field

from apps.warehouse.schemas import WarehouseSchema
from apps.pickup_point.schemas import PickUpPointSimpleSchema
from apps.users.models import MobileUser, WebUser
from apps.utils.enums import RoleType, GenderType


class MobileUserCreateSchema(Schema):
    email: EmailStr
    phone_number: str
    password: str
    first_name: str
    last_name: str
    father_name: str | None = None


class MobileUserUpdateSchema(Schema):
    phone_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    father_name: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[GenderType] = None


class UserPasswordUpdateSchema(Schema):
    current_password: str
    new_password: str


class MobileUserLoginSchema(Schema):
    email: EmailStr
    password: str


class MobileUserSchema(ModelSchema):
    email: str = Field(..., alias='user.username')
    avatar_id: int = Field(None, alias='avatar.id')
    avatar_url: str = Field(None, alias='avatar.image')

    class Meta:
        model = MobileUser
        fields = (
            'id',
            'profile_photo',
            'phone_number',
            'first_name',
            'last_name',
            'father_name',
            'birth_date',
            'gender'
        )


class MobileUserSimpleSchema(ModelSchema):
    class Meta:
        model = MobileUser
        fields = (
            'phone_number',
            'first_name',
            'last_name',
            'father_name',
        )


class WebUserCreateSchema(Schema):
    username: str
    password: str
    phone_number: str
    role: RoleType
    warehouse_id: Optional[int] = None
    pickup_point_id: Optional[int] = None


class WebUserLoginSchema(Schema):
    username: str
    password: str


class WebUserSchema(ModelSchema):
    username: str = Field(..., alias='user.username')
    assigned_warehouse: Optional[WarehouseSchema] = Field(None, alias='assignment.warehouse')
    assigned_pickup_point: Optional[PickUpPointSimpleSchema] = Field(None, alias='assignment.pickup_point')

    class Meta:
        model = WebUser
        fields = ('id', 'phone_number', 'role')
