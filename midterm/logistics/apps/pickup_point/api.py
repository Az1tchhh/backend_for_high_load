from django.http import JsonResponse
from ninja import Query
from ninja_extra import api_controller, ControllerBase, route, status
from ninja_extra.permissions import AllowAny
from django.utils.translation import gettext_lazy as _
from apps.country.filters import CityFilterSchema
from apps.country.models import City
from apps.orders.schemas import TrackNumberSchema
from apps.pickup_point.schemas import PickUpPointSchema
from apps.pickup_point.filters import PickUpPointFilterSchema
from apps.pickup_point.models import PickUpPoint
from apps.pickup_point.schemas import PickUpPointCreateSchema, PickUpPointUpdateSchema, PickUpPointCitiesSchema
from apps.pickup_point.services import create_pickup_point, update_pickup_point, assign_order_to_cell
from apps.utils.exceptions import ValidationException


@api_controller('pickup-point/', tags=['pickup-point'], permissions=[AllowAny])
class PickUpPointController(ControllerBase):
    @route.get('/', response=list[PickUpPointSchema])
    def list_pickup_points(self, filters: PickUpPointFilterSchema = Query(...)) -> list[PickUpPointSchema]:
        pickup_points = PickUpPoint.objects.all()
        pickup_points = filters.filter(pickup_points)
        return pickup_points

    @route.get('/{int:pickup_point_id}/')
    def get_pickup_point(self, pickup_point_id: int) -> PickUpPointSchema:
        pickup_point = self.get_object_or_exception(PickUpPoint, id=pickup_point_id)
        return PickUpPointSchema.from_orm(pickup_point)

    @route.post('/')
    def create_pickup_point(self, data: PickUpPointCreateSchema) -> PickUpPointSchema:
        pickup_point = create_pickup_point(data.dict(exclude_unset=True))
        return PickUpPointSchema.from_orm(pickup_point)

    @route.put('/{int:pickup_point_id}/')
    def update_pickup_point(self, pickup_point_id: int, data: PickUpPointUpdateSchema) -> PickUpPointSchema:
        pickup_point = self.get_object_or_exception(PickUpPoint, id=pickup_point_id)
        updated_pickup_point = update_pickup_point(pickup_point.pk, data.dict(exclude_unset=True))
        return PickUpPointSchema.from_orm(updated_pickup_point)

    @route.delete('/{int:pickup_point_id}/')
    def delete_pickup_point(self, pickup_point_id: int):
        pickup_point = self.get_object_or_exception(PickUpPoint, id=pickup_point_id)
        pickup_point.delete()
        return {"success": True}

    @route.get('cities/', response=list[PickUpPointCitiesSchema])
    def get_city_pickup_points(self, city_filters: CityFilterSchema = Query(...)):
        cities = City.objects.all()
        cities = city_filters.filter(cities)
        city_pickup_points = []
        for city in cities:
            pick_up_points = PickUpPoint.objects.filter(city_id=city.id)
            city_pickup_points.append({
                "city": city,
                "pick_up_points": pick_up_points
            })
        return city_pickup_points

    @route.post('assign-order-to-cell/')
    def assign_order_to_cell_endpoint(self, request, payload: TrackNumberSchema):
        track_number = payload.track_number
        if not track_number:
            raise ValidationException(_("Track number is required."))

        cell = assign_order_to_cell(track_number, request)
        return JsonResponse({"message": cell.cell_number}, status=status.HTTP_200_OK)
