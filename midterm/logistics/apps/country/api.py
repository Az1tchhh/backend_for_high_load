from typing import List

from ninja import Query
from ninja_extra import api_controller, ControllerBase, route
from ninja_extra.permissions import AllowAny

from apps.country.models import Country, City
from apps.country.filters import CountryFilterSchema, CityFilterSchema
from apps.country.schemas import CountrySchema, CountryCreateSchema, CityCreateSchema, CityUpdateSchema, CitySchema


@api_controller('country/', tags=['country'], permissions=[AllowAny])
class CountryController(ControllerBase):
    @route.get('/', response=list[CountrySchema])
    def list_countries(self, filters: CountryFilterSchema = Query(...)) -> list[CountrySchema]:
        countries = Country.objects.all()
        countries = filters.filter(countries)
        return countries

    @route.get('/{int:country_id}/')
    def get_country(self, country_id: int) -> CountrySchema:
        country = self.get_object_or_exception(Country, id=country_id)
        return CountrySchema.from_orm(country)

    @route.post('/')
    def create_country(self, data: CountryCreateSchema) -> CountrySchema:
        country = Country.objects.create(**data.dict())
        return CountrySchema.from_orm(country)

    @route.put('/{int:country_id}/')
    def update_country(self, country_id: int, data: CountryCreateSchema) -> CountrySchema:
        country = self.get_object_or_exception(Country, id=country_id)
        for attr, value in data.dict().items():
            setattr(country, attr, value)
        country.save()
        return CountrySchema.from_orm(country)

    @route.delete('/{int:country_id}/')
    def delete_country(self, country_id: int):
        country = self.get_object_or_exception(Country, id=country_id)
        country.delete()
        return {"success": True}


@api_controller('city/', tags=['city'], permissions=[AllowAny])
class CityController(ControllerBase):
    @route.get('/', response=List[CitySchema])
    def list_cities(self, filters: CityFilterSchema = Query(...)) -> list[CitySchema]:
        cities = City.objects.all()
        cities = filters.filter(cities)
        return cities

    @route.get('/{int:city_id}/')
    def get_city(self, city_id: int) -> CitySchema:
        city = self.get_object_or_exception(City, id=city_id)
        return CitySchema.from_orm(city)

    @route.post('/')
    def create_city(self, data: CityCreateSchema) -> CitySchema:
        city = City.objects.create(**data.dict())
        return CitySchema.from_orm(city)

    @route.put('/{int:city_id}/')
    def update_city(self, city_id: int, data: CityUpdateSchema) -> CitySchema:
        city = self.get_object_or_exception(City, id=city_id)
        for attr, value in data.dict(exclude_unset=True).items():
            setattr(city, attr, value)
        city.save()
        return CitySchema.from_orm(city)

    @route.delete('/{int:city_id}/')
    def delete_city(self, city_id: int):
        city = self.get_object_or_exception(City, id=city_id)
        city.delete()
        return {"success": True}
