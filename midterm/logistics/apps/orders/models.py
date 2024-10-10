from django.db import models
from django.utils import timezone

from apps.utils.enums import CurrencyChoices, OrderStatus
from apps.utils.services import upload_to


def order_barcode_upload(instance, filename):
    return upload_to(instance, 'order_barcode', filename)


class Order(models.Model):
    track_number = models.CharField(max_length=255, null=True, unique=True)
    currency = models.CharField(choices=CurrencyChoices.choices, default=CurrencyChoices.USD)
    comment = models.CharField(max_length=255, null=True)
    warehouse = models.ForeignKey(to='warehouse.Warehouse', on_delete=models.PROTECT, null=False)
    pickup_point = models.ForeignKey(to='pickup_point.PickUpPoint', on_delete=models.PROTECT, null=False)
    receiver = models.ForeignKey(to='users.MobileUser', on_delete=models.PROTECT, null=False)
    status = models.CharField(choices=OrderStatus.choices, default='introduced')
    tare = models.ForeignKey(to='warehouse.Tare', on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='orders')
    cell = models.ForeignKey(to='pickup_point.Cell', on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='orders')
    weight = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    shipping_price = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)

    @property
    def total_sum(self):
        return sum(item.sum for item in self.items.all())

    @property
    def warehouse_name(self):
        return self.warehouse.name


class OrderLocation(models.Model):
    order = models.OneToOneField(to='orders.Order', on_delete=models.CASCADE, null=False, related_name='location')
    at_warehouse = models.ForeignKey(to='warehouse.Warehouse', on_delete=models.CASCADE, null=True, blank=True)
    at_pickup_point = models.ForeignKey(to='pickup_point.PickUpPoint', on_delete=models.CASCADE, null=True, blank=True)


class OrderItem(models.Model):
    name = models.CharField(max_length=255, null=False)
    amount = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    comment = models.CharField(max_length=255, null=True)
    order = models.ForeignKey(to=Order, on_delete=models.CASCADE, null=False, related_name='items')

    @property
    def sum(self):
        return self.price * self.amount


class OrderCode(models.Model):
    order = models.OneToOneField(to=Order, on_delete=models.CASCADE, null=False, related_name='code')
    start_date = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField()
    code = models.CharField()


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(choices=OrderStatus.choices, max_length=50)
    at_pickup_point = models.ForeignKey(to='pickup_point.PickUpPoint', on_delete=models.CASCADE, null=True, blank=True)
    at_warehouse = models.ForeignKey(to='warehouse.Warehouse', on_delete=models.CASCADE, null=True, blank=True)
    changed_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.order.id} - {self.status} ({self.changed_at})"
