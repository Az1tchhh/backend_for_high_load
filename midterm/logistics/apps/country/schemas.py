from typing import Optional

from ninja import Schema


class CountrySchema(Schema):
    id: int
    name: str


class CountryCreateSchema(Schema):
    name: str


class CitySchema(Schema):
    id: int
    country_id: int
    name: str


class CityCreateSchema(Schema):
    country_id: int
    name: str


class CityUpdateSchema(Schema):
    country_id: Optional[int] = None
    name: Optional[str] = None