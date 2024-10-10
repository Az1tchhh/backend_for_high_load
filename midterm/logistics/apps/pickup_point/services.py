from django.db import transaction

from django.utils.translation import gettext_lazy as _
from apps.orders.models import Order
from apps.orders.services import change_order_status
from apps.pickup_point.models import PickUpPoint, Cell
from apps.utils.consts import MAX_ORDERS_FOR_CELL
from apps.utils.enums import OrderStatus
from apps.utils.exceptions import ValidationException


@transaction.atomic
def create_pickup_point(data):
    max_order_for_cell = data.pop('max_order_for_cell', MAX_ORDERS_FOR_CELL)
    if data.get('nds_payer'):
        if not data.get('nds_payer_certificate'):
            raise ValidationException(_('Provide VAT certificate.'))
    pickup_point = PickUpPoint.objects.create(**data)
    for i in range(pickup_point.cells_in_stock):
        cell_number = i + 1
        Cell.objects.create(pickup_point=pickup_point, cell_number=cell_number, max_orders=max_order_for_cell)

    return pickup_point


def update_pickup_point(pk, data):
    if data.get('nds_payer'):
        if not data.get('nds_payer_certificate'):
            raise ValidationException(_('Provide VAT certificate.'))
    pickup_point = PickUpPoint.objects.filter(pk=pk).first()
    if not pickup_point:
        raise ValidationException('Pickup point not found.')
    for attr, value in data.items():
        setattr(pickup_point, attr, value)
    pickup_point.save()
    return pickup_point


def assign_order_to_cell(track_number, request):
    web_user = request.auth.web_user
    order = Order.objects.filter(track_number=track_number).first()

    if not order:
        raise ValidationException(_("Order not found."))

    if not hasattr(web_user, 'assignment'):
        raise ValidationException(_("Web user is not allowed to perform this action."))

    assignment = web_user.assignment
    if not assignment.pickup_point:
        raise ValidationException(_("Web user is not assigned to any valid pickup point."))

    available_cell = Cell.objects.filter(pickup_point=assignment.pickup_point, user=order.receiver).first()

    if not available_cell:
        available_cell = Cell.objects.filter(is_full=False, user__isnull=True, orders__isnull=True).first()

    if available_cell is None:
        raise ValidationException(_("No empty cell."))
    available_cell.user = order.receiver
    order.cell = available_cell
    change_order_status(order, OrderStatus.AT_PICKUP_POINT)
    order.save()
    # update_cell_status(available_cell)
    return available_cell


def update_cell_status(cell):
    max_orders_per_cell = cell.max_orders
    if cell.orders.count() >= max_orders_per_cell:
        cell.is_full = True
    else:
        cell.is_full = False

    if cell.orders.filter(receiver=cell.user).count() == 0:
        cell.user = None
        cell.is_full = False

    cell.save()
