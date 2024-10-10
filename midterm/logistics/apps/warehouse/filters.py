from typing import Optional

from ninja import FilterSchema
from pydantic import Field

from apps.utils.enums import WarehouseType


class WarehouseFilterSchema(FilterSchema):
    city_id: Optional[int] = None
    name: Optional[str] = Field(None, q='name__icontains')
    address: Optional[str] = Field(None, q='address__icontains')
    type: Optional[WarehouseType] = None
