from datetime import timedelta, datetime

from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.orders.models import Order, OrderItem, OrderCode, OrderStatusHistory, OrderLocation
from apps.orders.schemas import CodeSchema, CalculateShippingPriceSchema
from apps.users.models import User, WebUser
from apps.utils.enums import OrderStatus, WEIGHT_PRICE_COEFFICIENT, CURRENCY_CODES
from apps.utils.exceptions import ValidationException
from apps.utils.services import generate_unique_code, generate_order_barcode, generate_barcode
from apps.wallets.models import Wallet
from apps.warehouse.models import Tare


def create_order(data, user):
    items = data.pop('items')
    order = Order.objects.create(**data, receiver=user, status=OrderStatus.INTRODUCED)
    OrderStatusHistory.objects.create(order=order, status=OrderStatus.INTRODUCED)
    for item in items:
        OrderItem.objects.create(**item, order=order)

    location = OrderLocation.objects.create(order=order)
    return order


def update_order(pk, data):
    order = Order.objects.filter(pk=pk).first()
    if not order:
        raise ValueError("Order not found")
    items = data.pop('items')
    for attr, value in data.items():
        setattr(order, attr, value)
    order.save()
    excluded_item_ids = []
    for item in items:
        if item.get('id') is not None:
            order_item = OrderItem.objects.filter(pk=item.get('id')).first()
            for attr, value in item.items():
                setattr(order_item, attr, value)
            excluded_item_ids.append(order_item.id)
        else:
            order.save()
            order_item = OrderItem.objects.create(**item, order=order)
            excluded_item_ids.append(order_item.id)
        order_item.save()
    order.items.exclude(id__in=excluded_item_ids).delete()
    order.save()
    return order


@transaction.atomic
def change_order_status(order: Order, new_status: OrderStatus, web_user: WebUser = None):
    try:
        if order is None:
            raise ValidationException(_("Order not found."))
        new_status = providing_autopayment_options(order, new_status)
        print(new_status)
        set_location_and_status_history(order, web_user, new_status)

        return order
    except Order.DoesNotExist:
        raise ValidationException(_("Order not found."))


def providing_autopayment_options(order: Order, new_status: OrderStatus):
    if new_status == OrderStatus.WAITING_FOR_PAYMENT:
        paid_in_order_status_history = OrderStatusHistory.objects.filter(order=order, status=OrderStatus.PAID).first()
        if paid_in_order_status_history is not None:
            raise ValidationException(_("Order already paid."))
    elif new_status == OrderStatus.AT_PICKUP_POINT:
        paid_in_order_status_history = OrderStatusHistory.objects.filter(order=order, status=OrderStatus.PAID).first()
        if paid_in_order_status_history is None:
            try:
                pay_for_order(order, order.receiver.user)
            except Exception as e:
                print(str(e))
                new_status = OrderStatus.WAITING_FOR_PAYMENT
                pass
    return new_status


def set_location_and_status_history(order: Order, web_user: WebUser, new_status: OrderStatus):
    order_status_history = OrderStatusHistory.objects.create(order=order, status=new_status)
    order.status = new_status

    order_location = order.location

    if web_user:
        if hasattr(web_user, 'assignment'):
            warehouse = web_user.assignment.warehouse
            pickup_point = web_user.assignment.pickup_point

            order_location.at_warehouse = warehouse
            order_location.at_pickup_point = pickup_point
            if pickup_point:
                order_location.order.tare = None
                order_status_history.at_pickup_point = pickup_point
            elif warehouse:
                order_location.order.cell = None
                order_status_history.at_warehouse = warehouse

    order_status_history.save()
    order_location.save()
    order.save()
    return


def get_order_last_status(order: Order):
    order_status_history = OrderStatusHistory.objects.filter(order_id=order.id).order_by('-changed_at').first()
    return order_status_history


def get_order_by_code(payload: CodeSchema):
    data = payload.dict()
    code = data.get('code')
    order_code = OrderCode.objects.filter(code=code).first()
    if order_code is None:
        raise ValidationException(_("Order not found."))
    if order_code.expiration_date < timezone.now():
        raise ValidationException(_("Code is expired. Regenerate it."))
    return order_code.order


@transaction.atomic
def create_or_retrieve_order_code(order: Order):
    if order is None:
        raise ValidationException(_("Order not found."))

    if order.status == OrderStatus.WAITING_FOR_PAYMENT:
        raise ValidationException(_("Order not paid. Waiting for Payment."))
    order_code = OrderCode.objects.filter(order=order).first()
    if not order_code:
        new_order_code = create_order_code(order)
        return new_order_code
    else:
        if order_code.expiration_date < timezone.now():
            order_code = update_order_code(order)
    return order_code


def get_barcode_for_receival(order: Order):
    if order is None:
        raise ValidationException(_("Order not found."))
    order_code = create_or_retrieve_order_code(order)
    barcode = generate_order_barcode(order_code.code)
    return barcode


@transaction.atomic
def create_order_code(order: Order):
    code = generate_unique_code()
    expiration_date = datetime.now() + timedelta(minutes=5)
    order_code = OrderCode.objects.create(
        order=order,
        expiration_date=expiration_date,
        code=code
    )
    return order_code


@transaction.atomic
def update_order_code(order: Order):
    code = generate_unique_code()
    expiration_date = datetime.now() + timedelta(minutes=5)
    OrderCode.objects.filter(
        order=order
    ).update(expiration_date=expiration_date, code=code)
    order_code = OrderCode.objects.filter(order=order).first()
    return order_code


@transaction.atomic
def pay_for_order(order: Order, user: User):
    if order is None:
        raise ValidationException(_("Order not found."))
    paid_in_order_status_history = OrderStatusHistory.objects.filter(order=order, status=OrderStatus.PAID).first()
    print(paid_in_order_status_history)
    if paid_in_order_status_history is not None:
        raise ValidationException(_("Order already paid."))

    wallet = Wallet.objects.filter(user=user).first()
    if wallet is None:
        raise ValidationException(_("Wallet not found. You cannot get the code without payment."))
    if order.shipping_price is None:
        raise ValidationException(_("Shipping price not set."))

    shipping_price = order.shipping_price * CURRENCY_CODES['usd']
    if wallet.balance - shipping_price < 0:
        raise ValidationException(_("Your balance is not enough. {shipping_price} {currency}.").format(
            shipping_price=shipping_price,
            currency=CURRENCY_CODES[order.currency]
        ))

    wallet.balance -= shipping_price
    wallet.save()

    change_order_status(order, OrderStatus.PAID)
    return order


class OrderService:
    def get_order_by_track_number(self, track_number: str):
        raise NotImplemented

    def get_barcode_for_order(self, pk: int):
        raise NotImplemented

    def calculate_shipping_price(self, order: Order, payload: CalculateShippingPriceSchema):
        raise NotImplemented


class OrderServiceImpl(OrderService):
    def get_order_by_track_number(self, track_number: str):
        order = Order.objects.filter(track_number=track_number).first()
        if order is None:
            raise ValidationException(_("Order not found."))
        return order

    def get_barcode_for_order(self, pk: int):
        order = Order.objects.filter(id=pk).first()
        if order is None:
            raise ValidationException(_("Order not found."))
        barcode = generate_barcode(order.track_number)
        return barcode

    def calculate_shipping_price(self, order: Order, payload: CalculateShippingPriceSchema):
        data = payload.dict()
        weight = data.get('weight')
        coefficient = data.get('coefficient', None)
        confirmed = data.pop('confirmed', None)
        if coefficient is None:
            coefficient = WEIGHT_PRICE_COEFFICIENT[order.currency]
            data['coefficient'] = coefficient
        shipping_price = weight * coefficient
        data['shipping_price'] = shipping_price
        if confirmed:
            order.weight = weight
            order.shipping_price = shipping_price
            order.save()
        return data


def assign_order_to_tare(track_number, request):
    web_user = request.auth.web_user
    order = Order.objects.filter(track_number=track_number).first()

    if not order:
        raise ValidationException(_("Order not found."))

    if not hasattr(web_user, 'assignment'):
        raise ValidationException(_("Web user is not allowed to perform this action."))

    assignment = web_user.assignment
    if not assignment.warehouse:
        raise ValidationException(_("Web user has no warehouse."))

    available_tare = Tare.objects.filter(
        warehouse_id=assignment.warehouse.id
    ).distinct().first()

    if not available_tare:
        raise ValidationException(_("You do not have a tare. Create one."))

    order.tare = available_tare
    change_order_status(order, OrderStatus.AT_WAREHOUSE)
    order.save()

    # update_tare_status(available_tare)

    return available_tare


def update_tare_status(tare):
    max_orders_per_tare = tare.max_orders
    if tare.orders.count() >= max_orders_per_tare:
        tare.is_full = True
        tare.save()
