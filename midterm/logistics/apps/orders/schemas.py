from _decimal import Decimal
from datetime import datetime
from typing import Optional, List

from ninja import Schema, ModelSchema
from pydantic import Field

from apps.orders.models import OrderStatusHistory, OrderLocation
from apps.pickup_point.schemas import CellSchema, PickUpPointOrderSchema
from apps.users.schemas import MobileUserSimpleSchema
from apps.utils.enums import CurrencyChoices, OrderStatus
from apps.warehouse.schemas import TareSchema


class OrderItemSchema(Schema):
    id: int
    name: str
    amount: int
    price: Decimal
    comment: Optional[str]
    order_id: int
    sum: Decimal


class OrderItemCreateSchema(Schema):
    name: str
    amount: int
    price: Decimal
    comment: Optional[str] = None


class OrderItemUpdateSchema(Schema):
    id: Optional[int] = None
    name: Optional[str] = None
    amount: Optional[int] = None
    price: Optional[Decimal] = None
    comment: Optional[str] = None


class OrderItemInOrderSchema(Schema):
    id: int
    amount: int
    name: str
    price: Decimal
    sum: Decimal
    comment: str = None


class OrderLocationSchema(ModelSchema):
    at: Optional[str] = None
    cell: Optional[CellSchema] = Field(None, alias='order.cell')
    tare: Optional[TareSchema] = Field(None, alias='order.tare')

    class Meta:
        model = OrderLocation
        fields = (
            'at_warehouse',
            'at_pickup_point',
        )

    @staticmethod
    def resolve_at(order_location):
        if order_location.at_warehouse:
            return order_location.at_warehouse.name
        elif order_location.at_pickup_point:
            return order_location.at_pickup_point.name
        return 'Delivering'


class OrderSchema(Schema):
    id: int
    track_number: str
    currency: str
    comment: str | None
    warehouse_id: int
    warehouse_name: str
    pickup_point: PickUpPointOrderSchema
    receiver_id: int
    receiver: MobileUserSimpleSchema
    status: str
    status_changed_time: Optional[datetime] = None
    is_paid: bool
    location: OrderLocationSchema
    items: List[OrderItemInOrderSchema]
    total_sum: Decimal
    weight: Optional[Decimal]
    shipping_price: Optional[Decimal]

    @staticmethod
    def resolve_status_changed_time(order):
        order_status_history = OrderStatusHistory.objects.filter(order_id=order.id).order_by('-changed_at').first()
        last_changed_time = order_status_history.changed_at
        return last_changed_time

    @staticmethod
    def resolve_is_paid(order):
        is_order_paid = OrderStatusHistory.objects.filter(order_id=order.id, status=OrderStatus.PAID).exists()
        if is_order_paid:
            return True
        return False


class OrderCreateSchema(Schema):
    track_number: str
    currency: Optional[CurrencyChoices] = 'usd'
    comment: Optional[str] = None
    warehouse_id: int
    pickup_point_id: int
    items: List[OrderItemCreateSchema]


class OrderUpdateSchema(Schema):
    track_number: Optional[str] = None
    currency: Optional[str] = 'usd'
    comment: Optional[str] = None
    warehouse_id: Optional[int] = None
    pickup_point_id: Optional[int] = None
    items: Optional[List[OrderItemUpdateSchema]]


class LastOrderStatusSchema(ModelSchema):
    order_id: int = Field(..., alias='order.id')
    at_pickup_point_name: str = Field(None, alias='at_pickup_point.name')
    at_warehouse_name: str = Field(None, alias='at_warehouse.name')

    class Meta:
        model = OrderStatusHistory
        fields = (
            'id',
            'status',
            'changed_at',
            'at_pickup_point',
            'at_warehouse',
        )


class OrderCodeSchema(Schema):
    code: str
    expiration_date: datetime


class CodeSchema(Schema):
    code: str


class ShippingAddressSchema(Schema):
    id: int
    user_id: int
    city_id: int
    address: str


class ShippingAddressCreateSchema(Schema):
    user_id: int
    city_id: int
    address: str

class StatusChangeHistorySchema(ModelSchema):
    at: Optional[str] = None

    class Meta:
        model = OrderStatusHistory
        fields = (
            'id',
            'status',
            'at_pickup_point',
            'at_warehouse',
            'changed_at',
        )

    @staticmethod
    def resolve_at(order_status_history):
        if order_status_history.at_warehouse:
            return order_status_history.at_warehouse.name
        elif order_status_history.at_pickup_point:
            return order_status_history.at_pickup_point.name
        return 'Delivering'


class TrackNumberSchema(Schema):
    track_number: str


class CalculateShippingPriceSchema(Schema):
    weight: Decimal
    coefficient: Decimal = None
    confirmed: bool


class CalculatedShippingPriceSchema(Schema):
    weight: Decimal
    coefficient: Decimal
    shipping_price: Decimal
