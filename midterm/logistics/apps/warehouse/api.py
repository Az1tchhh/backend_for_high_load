from ninja import Query
from ninja_extra import api_controller, route, ControllerBase
from ninja_extra.permissions import AllowAny

from apps.warehouse.filters import WarehouseFilterSchema
from apps.warehouse.models import Warehouse
from apps.warehouse.schemas import WarehouseSchema, WarehouseCreateSchema, WarehouseUpdateSchema
from apps.warehouse.services import create_warehouse


@api_controller('warehouse/', tags=['warehouse'], permissions=[AllowAny])
class WarehouseController(ControllerBase):
    @route.get('/', response=list[WarehouseSchema])
    def list_warehouses(self, filters: WarehouseFilterSchema = Query(...)) -> list[WarehouseSchema]:
        warehouses = Warehouse.objects.all()
        warehouses = filters.filter(warehouses)
        return warehouses

    @route.get('/{int:warehouse_id}/')
    def get_warehouse(self, warehouse_id: int) -> WarehouseSchema:
        warehouse = self.get_object_or_exception(Warehouse, id=warehouse_id)
        return WarehouseSchema.from_orm(warehouse)

    @route.post('/')
    def create_warehouse(self, data: WarehouseCreateSchema) -> WarehouseSchema:
        warehouse = create_warehouse(data.dict(exclude_unset=True))
        return WarehouseSchema.from_orm(warehouse)

    @route.put('/{int:warehouse_id}/')
    def update_warehouse(self, warehouse_id: int, data: WarehouseUpdateSchema) -> WarehouseSchema:
        warehouse = self.get_object_or_exception(Warehouse, id=warehouse_id)
        for attr, value in data.dict(exclude_unset=True).items():
            setattr(warehouse, attr, value)
        warehouse.save()
        return WarehouseSchema.from_orm(warehouse)

    @route.delete('/{int:warehouse_id}/')
    def delete_warehouse(self, warehouse_id: int):
        warehouse = self.get_object_or_exception(Warehouse, id=warehouse_id)
        warehouse.delete()
        return {"success": True}
