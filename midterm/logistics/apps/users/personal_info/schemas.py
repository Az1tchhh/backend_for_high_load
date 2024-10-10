from datetime import date
from typing import Optional, Union

from ninja import ModelSchema, Schema
from pydantic import Field

from apps.users.personal_info.models import MyAddress, PersonalInfo


class MyAddressSchema(ModelSchema):
    country: str = Field(..., alias='city.country.name')
    city: str = Field(..., alias='city.name')

    class Meta:
        model = MyAddress
        fields = (
            'id',
            'address_name',
            'address',
        )


class MyAddressRetrieveSchema(ModelSchema):
    country: str = Field(..., alias='city.country.name')
    country_id: int = Field(..., alias='city.country.id')
    city: str = Field(..., alias='city.name')
    city_id: int = Field(..., alias='city.id')

    class Meta:
        model = MyAddress
        fields = (
            'id',
            'address_name',
            'address',
        )


class MyAddressCreateSchema(Schema):
    address_name: str
    city_id: int
    address: str


class MyAddressUpdateSchema(Schema):
    address_name: Optional[str] = None
    city_id: Optional[int] = None
    address: Optional[str] = None


class PersonalInfoSchema(ModelSchema):
    citizenship: str = Field(None, alias='citizenship.name')
    citizenship_id: int = Field(None, alias='citizenship.id')

    class Meta:
        model = PersonalInfo
        fields = (
            'document_number',
            'date_of_issue',
            'validity_period',
            'iin',
            'given_by'
        )
        fields_optional = (
            'document_number',
            'date_of_issue',
            'validity_period',
            'iin',
            'given_by'
        )


class PersonalInfoCreateSchema(Schema):
    citizenship_id: int
    document_number: str = Field(..., max_length=9)
    date_of_issue: date
    validity_period: date
    iin: str = Field(..., max_length=12)
    given_by: str


class PersonalInfoUpdateSchema(Schema):
    citizenship_id: Optional[int] = None
    document_number: Optional[str] = Field(None, max_length=9)
    date_of_issue: Optional[date] = None
    validity_period: Optional[date] = None
    iin: Optional[str] = Field(None, max_length=12)
    given_by: Optional[str] = None
