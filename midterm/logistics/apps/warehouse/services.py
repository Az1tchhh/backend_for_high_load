from django.db import transaction

from apps.utils.consts import MAX_ORDERS_FOR_TARE
from apps.warehouse.models import Warehouse, Tare


@transaction.atomic
def create_warehouse(data):
    max_orders_for_tare = data.pop('max_orders_for_tare', MAX_ORDERS_FOR_TARE)
    warehouse = Warehouse.objects.create(**data)
    Tare.objects.create(tare_number=warehouse.id, max_orders=max_orders_for_tare, warehouse=warehouse)
    return warehouse
