from django.db import models

from apps.utils.enums import WarehouseType


# Create your models here.

class Warehouse(models.Model):
    name = models.CharField(max_length=255, null=False)
    address = models.CharField(max_length=255, null=False)
    city = models.ForeignKey(to='country.City', on_delete=models.CASCADE, null=False)
    type = models.CharField(choices=WarehouseType.choices, default='warehouse')
    can_evaluate_order = models.BooleanField(default=False, null=False)


class Tare(models.Model):
    is_full = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    max_orders = models.PositiveIntegerField(null=False)
    tare_number = models.PositiveIntegerField(null=False)
    warehouse = models.OneToOneField(to=Warehouse, on_delete=models.CASCADE, null=True, related_name='tare')

    def __str__(self):
        return f"Tare {self.id}"

    @property
    def assigned_pickup_points(self):
        """Возвращает список уникальных PickupPoint, для которых предназначены заказы в этой таре."""
        return list(set(order.pickup_point for order in self.orders.all()))