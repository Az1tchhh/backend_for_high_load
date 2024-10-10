from typing import Optional

from ninja import FilterSchema
from pydantic import Field

from apps.utils.enums import PickUpPointStatus


class PickUpPointFilterSchema(FilterSchema):
    city_id: Optional[int] = None
    name: Optional[str] = Field(None, q='name__icontains')
    address: Optional[str] = Field(None, q='address__icontains')
    full_name: Optional[str] = Field(None, q='full_name__icontains')
    status: Optional[PickUpPointStatus] = None