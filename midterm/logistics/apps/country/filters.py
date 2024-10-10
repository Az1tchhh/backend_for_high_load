from typing import Optional

from ninja import FilterSchema
from pydantic import Field


class CountryFilterSchema(FilterSchema):
    name: Optional[str] = Field(None, q='name__icontains')


class CityFilterSchema(FilterSchema):
    country_id: Optional[int] = None
    name: Optional[str] = Field(None, q='name__icontains')
