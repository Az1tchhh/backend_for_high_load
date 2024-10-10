from django.db.models import Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.translation import gettext as _  # Import gettext for localization
from injector import inject
from typing import Optional, List

from ninja_extra import api_controller, ControllerBase, route, paginate, status
from ninja_extra.pagination import PageNumberPaginationExtra
from ninja_extra.permissions import AllowAny

from apps.orders.models import Order, OrderStatusHistory
from apps.orders.schemas import OrderSchema, OrderCreateSchema, OrderUpdateSchema, \
    OrderCodeSchema, CodeSchema, \
    StatusChangeHistorySchema, LastOrderStatusSchema, TrackNumberSchema, \
    CalculateShippingPriceSchema, CalculatedShippingPriceSchema
from apps.orders.services import create_order, update_order, OrderService, \
    change_order_status, pay_for_order, create_or_retrieve_order_code, get_order_by_code, \
    get_barcode_for_receival, get_order_last_status, assign_order_to_tare
from apps.users.permissions import IsWebUser
from apps.utils.enums import OrderStatus, RoleType
from apps.utils.exceptions import ValidationException


@api_controller('order/', tags=['order'], permissions=[AllowAny])
class OrderController(ControllerBase):

    def get_queryset(self):
        user = self.context.request.auth
        queryset = Order.objects.all()
        if hasattr(user, 'web_user'):
            if user.web_user.role == RoleType.ADMIN:
                pass
            else:
                if user.web_user.assignment.warehouse:
                    queryset = queryset.filter(Q(location__at_warehouse__id=user.web_user.assignment.warehouse.id))
                elif user.web_user.assignment.pickup_point:
                    queryset = queryset.filter(location__at_pickup_point__id=user.web_user.assignment.pickup_point.id)
        else:
            queryset = queryset.filter(receiver=user.mobile_user)

        return queryset

    @inject
    def __init__(self, order_service: OrderService):
        self.order_service = order_service

    @route.get('/')
    @paginate(PageNumberPaginationExtra, page_size=10)
    def list_orders(self, status: Optional[str] = None):
        orders = self.get_queryset()
        if status:
            orders = orders.filter(status=status)
        return [OrderSchema.from_orm(order) for order in orders]

    @route.get('/{int:order_id}/', response=OrderSchema)
    def get_order(self, order_id: int) -> OrderSchema:
        queryset = self.get_queryset()
        order = queryset.filter(id=order_id).first()
        if order is None:
            raise ValidationException(_("Order does not exist."))
        return order

    @route.post('/')
    def create_order(self, data: OrderCreateSchema, request: HttpRequest) -> OrderSchema:
        user = request.auth.mobile_user
        order = create_order(data.dict(exclude_unset=True), user=user)
        return OrderSchema.from_orm(order)

    @route.put('/{int:order_id}/')
    def update_order(self, order_id: int, data: OrderUpdateSchema, request: HttpRequest) -> OrderSchema:
        queryset = self.get_queryset()
        order = queryset.filter(id=order_id).first()
        if order is None:
            raise ValidationException(_('Order not found.'))
        updated_order = update_order(order.pk, data.dict())
        return OrderSchema.from_orm(updated_order)

    @route.delete('/{int:order_id}/')
    def delete_order(self, order_id: int):
        queryset = self.get_queryset()
        order = queryset.filter(id=order_id).first()
        if order is None:
            raise ValidationException(_('Order not found.'))
        order.delete()
        return {"success": True}

    @route.put('{int:order_id}/status/', response=OrderSchema, permissions=[IsWebUser])
    def change_order_status(self, order_id: int, new_status: OrderStatus):
        order = Order.objects.filter(id=order_id).first()
        order = change_order_status(order, new_status, self.context.request.auth.web_user)
        return order

    @route.get('{int:order_id}/status-change-history/', response=List[StatusChangeHistorySchema])
    def status_change_history_list(self, order_id: int):
        change_history = OrderStatusHistory.objects.filter(order_id=order_id)
        return list(change_history)

    @route.post('by-code/', response=OrderSchema)
    def get_order_by_code(self, payload: CodeSchema):
        order = get_order_by_code(payload)
        return order

    @route.get('{int:order_id}/code/', response=OrderCodeSchema)
    def get_order_code(self, order_id: int):
        queryset = self.get_queryset()
        order = queryset.filter(id=order_id).first()
        order_code = create_or_retrieve_order_code(order)
        return order_code

    @route.get('{int:order_id}/receiving-barcode/')
    def get_receival_barcode(self, order_id: int):
        queryset = self.get_queryset()
        order = queryset.filter(id=order_id).first()
        barcode = get_barcode_for_receival(order)
        return HttpResponse(barcode, status=status.HTTP_200_OK)

    @route.post('{int:order_id}/pay/', response=OrderSchema)
    def pay_for_order(self, order_id: int):
        queryset = self.get_queryset()
        user = self.context.request.auth
        order = queryset.filter(id=order_id).first()
        order = pay_for_order(order, user)
        return order

    @route.get('by-track-number/', response=OrderSchema)
    def get_by_track_number(self, track_number: str):
        order = self.order_service.get_order_by_track_number(track_number)
        return order

    @route.post('{id}/generate-track-barcode/')
    def generate_track_barcode_for_order(self, id: int):
        barcode = self.order_service.get_barcode_for_order(id)
        return HttpResponse(barcode, status=status.HTTP_200_OK)

    @route.get('{id}/last-status/', response=LastOrderStatusSchema)
    def get_order_last_status(self, id: int):
        queryset = self.get_queryset()
        order = queryset.filter(id=id).first()
        last_status = get_order_last_status(order)
        return last_status

    @route.post('assign-order-to-tare/')
    def assign_order_to_tare(self, payload: TrackNumberSchema, request):
        track_number = payload.track_number
        if not track_number:
            raise ValidationException(_("Track number is required."))

        tare = assign_order_to_tare(track_number=track_number, request=request)
        return JsonResponse({"message": tare.tare_number}, status=status.HTTP_200_OK)

    @route.post('{id}/calculate-shipping-price/', response=CalculatedShippingPriceSchema, permissions=[IsWebUser])
    def calculcate_shipping_price(self, id: int, payload: CalculateShippingPriceSchema):
        user = self.context.request.auth
        if not user.web_user.assignment.warehouse.can_evaluate_order:
            raise ValidationException(_("You can not calculate shipping price on this warehouse."))
        queryset = self.get_queryset()
        order = queryset.filter(id=id).first()
        if order is None:
            raise ValidationException(_("Order does not exist."))
        return self.order_service.calculate_shipping_price(order, payload)
