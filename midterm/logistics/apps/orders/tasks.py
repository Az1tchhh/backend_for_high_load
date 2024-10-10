from celery import shared_task

from apps.orders.models import Order, OrderStatusHistory
from apps.orders.services import pay_for_order
from apps.users.models import User
from apps.utils.enums import OrderStatus


@shared_task
def pay_orders_automatically(user_id: int):
    user = User.objects.get(id=user_id)
    orders = Order.objects.filter(receiver=user.mobile_user, status=OrderStatus.AT_PICKUP_POINT)
    for order in orders:
        order_status_history = OrderStatusHistory.objects.filter(order=order).values_list(
            'status', flat=True)
        if OrderStatus.PAID in order_status_history:
            continue
        pay_for_order(order, user)
    return
