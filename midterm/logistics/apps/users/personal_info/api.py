from typing import List

from ninja_extra import api_controller, ControllerBase, route
from django.utils.translation import gettext_lazy as _
from apps.users.permissions import IsMobileUser
from apps.users.personal_info.schemas import MyAddressSchema, MyAddressCreateSchema, MyAddressUpdateSchema, \
    PersonalInfoSchema, PersonalInfoCreateSchema, PersonalInfoUpdateSchema, MyAddressRetrieveSchema
from apps.users.personal_info.services import get_address_by_user, create_address_for_user, update_user_address, \
    get_personal_info_by_user, create_personal_info_for_user, update_personal_info, delete_user_address, \
    delete_personal_info
from apps.utils.exceptions import ValidationException
from apps.utils.schemas import NoContentSchema


@api_controller('my_address/', tags=['personal_info'], permissions=[IsMobileUser])
class MyAddressController(ControllerBase):
    @route.get('', response=List[MyAddressSchema])
    def get(self):
        user = self.context.request.auth
        my_addresses = get_address_by_user(user)
        return my_addresses

    @route.get('{id}/', response=MyAddressRetrieveSchema)
    def retrieve(self, id: int):
        user = self.context.request.auth
        my_addresses = get_address_by_user(user)
        address = my_addresses.filter(id=id).first()
        if address is None:
            raise ValidationException(_("Address does not exist."))
        return address

    @route.post('', response=MyAddressSchema)
    def post(self, payload: MyAddressCreateSchema):
        user = self.context.request.auth
        my_new_address = create_address_for_user(user, payload)
        return my_new_address

    @route.patch('{id}/', response=MyAddressRetrieveSchema)
    def patch(self, id: int, payload: MyAddressUpdateSchema):
        user = self.context.request.auth
        updated_address = update_user_address(user, id, payload)
        return updated_address

    @route.delete('{id}/', response={204: NoContentSchema})
    def delete(self, id: int):
        user = self.context.request.auth
        delete_user_address(user, id)
        return 204


@api_controller('personal_info/', tags=['personal_info'], permissions=[IsMobileUser])
class PersonalInfoController(ControllerBase):

    @route.get('', response=PersonalInfoSchema)
    def get(self):
        user = self.context.request.auth
        my_personal_info = get_personal_info_by_user(user)
        return my_personal_info

    @route.post('', response=PersonalInfoSchema)
    def post(self, payload: PersonalInfoCreateSchema):
        user = self.context.request.auth
        new_personal_info = create_personal_info_for_user(user, payload)
        return new_personal_info

    @route.patch('', response=PersonalInfoSchema)
    def patch(self, payload: PersonalInfoUpdateSchema):
        user = self.context.request.auth
        updated_personal_info = update_personal_info(user, payload)
        return updated_personal_info

    @route.delete('', response={204: NoContentSchema})
    def delete(self):
        user = self.context.request.auth
        delete_personal_info(user)
        return 204
