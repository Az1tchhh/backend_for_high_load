from typing import Optional

from ninja import Schema, ModelSchema
from pydantic import Field, EmailStr

from apps.country.schemas import CitySchema
from apps.pickup_point.models import Cell
from apps.utils.enums import PickUpPointStatus


class PickUpPointOrderSchema(Schema):
    name: str
    address: str
    phone_number: str
    city: CitySchema


class PickUpPointSimpleSchema(Schema):
    id: int
    name: str
    address: str
    city_id: int
    city_name: str = Field(..., alias='city.name')


class CellSchema(ModelSchema):
    id: int
    pickup_point_id: int

    class Meta:
        model = Cell
        fields = (
            'cell_number',
            'max_orders',
            'is_full',
        )


class PickUpPointSchema(Schema):
    id: int
    city: CitySchema
    address: str
    name: str
    phone_number: str
    email: Optional[EmailStr] = None
    full_name: str
    juridical_form: str
    individual_identification_number: str
    online_banking_certificate: str
    nds_payer: bool
    nds_payer_certificate: Optional[str] = None
    cells_in_stock: int
    status: str


class PickUpPointCreateSchema(Schema):
    city_id: int
    address: str
    name: str
    phone_number: str
    email: Optional[EmailStr] = None
    full_name: str
    juridical_form: str
    individual_identification_number: str
    online_banking_certificate: str
    nds_payer: bool
    nds_payer_certificate: Optional[str] = None
    cells_in_stock: int = Field(..., gt=0)
    status: Optional[str] = PickUpPointStatus.INACTIVE
    # max_order_for_tare: Optional[int] = None
    max_order_for_cell: Optional[int] = Field(None, gt=0)


class PickUpPointUpdateSchema(Schema):
    city_id: Optional[int] = None
    address: Optional[str] = None
    name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    juridical_form: Optional[str] = None
    individual_identification_number: Optional[str] = None
    online_banking_certificate: Optional[str] = None
    nds_payer: Optional[bool] = None
    nds_payer_certificate: Optional[str] = None
    cells_in_stock: Optional[int] = Field(None, gt=0)
    status: Optional[str] = None
    max_order_for_cell: Optional[int] = Field(None, gt=0)


class PickUpPointCitiesSchema(Schema):
    city: CitySchema
    pick_up_points: list[PickUpPointSimpleSchema]
