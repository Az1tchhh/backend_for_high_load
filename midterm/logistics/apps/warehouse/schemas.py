from typing import Optional

from ninja import Schema, ModelSchema
from pydantic import Field

from apps.utils.enums import WarehouseType
from apps.warehouse.models import Tare


class WarehouseSchema(Schema):
    id: int
    name: str
    address: str
    city_id: int
    type: str
    can_evaluate_order: bool


class WarehouseCreateSchema(Schema):
    name: str
    address: str
    city_id: int
    type: WarehouseType
    can_evaluate_order: bool = False
    max_orders_for_tare: Optional[int] = Field(None, gt=0)


class WarehouseUpdateSchema(Schema):
    name: Optional[str] = None
    address: Optional[str] = None
    city_id: Optional[int] = None
    type: Optional[WarehouseType] = None
    can_evaluate_order: Optional[bool] = None


class TareSchema(ModelSchema):
    id: int
    warehouse_id: int

    class Meta:
        model = Tare
        fields = (
            'tare_number',
            'max_orders',
            'is_full',
        )
