from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _

from apps.users.models import User, MobileUser
from apps.users.personal_info.models import MyAddress, PersonalInfo
from apps.users.personal_info.schemas import MyAddressCreateSchema, MyAddressUpdateSchema, PersonalInfoCreateSchema, \
    PersonalInfoUpdateSchema
from apps.utils.exceptions import ValidationException


def get_address_by_user(user: User):
    if hasattr(user, 'mobile_user'):
        user_addresses = MyAddress.objects.filter(mobile_user=user.mobile_user)
        return user_addresses
    else:
        raise ValidationException(_("User must be a mobile user."))


@transaction.atomic
def create_address_for_user(user: User, payload: MyAddressCreateSchema):
    if hasattr(user, 'mobile_user'):
        data = payload.dict()
        address_name = data.get('address_name')
        if is_unique_address_name(user.mobile_user, address_name):
            address = MyAddress.objects.create(**data, mobile_user=user.mobile_user)
        else:
            raise ValidationException(_("Address name already exists."))
        return address
    else:
        raise ValidationException(_("User must be a mobile user."))


@transaction.atomic
def update_user_address(user: User, id, payload: MyAddressUpdateSchema):
    if hasattr(user, 'mobile_user'):
        data = payload.dict(exclude_unset=True)
        my_address = MyAddress.objects.filter(pk=id).first()
        if not my_address:
            raise ValidationException(_("This address does not exist."))

        for attr, value in data.items():
            setattr(my_address, attr, value)

        my_address.save()
        return my_address
    else:
        raise ValidationException(_("User must be a mobile user."))


@transaction.atomic
def delete_user_address(user: User, id):
    if hasattr(user, 'mobile_user'):
        mobile_user = user.mobile_user
        my_address = MyAddress.objects.filter(id=id, mobile_user=mobile_user).first()
        if my_address is None:
            raise ValidationException(_("This address does not exist."))
        my_address.delete()
        return


def is_unique_address_name(mobile_user: MobileUser, address_name: str):
    does_address_exist = MyAddress.objects.filter(
        mobile_user=mobile_user,
        address_name__iexact=address_name)
    if does_address_exist:
        return False
    return True


def get_personal_info_by_user(user: User):
    if hasattr(user, 'mobile_user'):
        personal_info = PersonalInfo.objects.filter(mobile_user=user.mobile_user).first()
        return personal_info
    else:
        raise ValidationException(_("User must be a mobile user."))


@transaction.atomic
def create_personal_info_for_user(user: User, payload: PersonalInfoCreateSchema):
    if hasattr(user, 'mobile_user'):
        mobile_user = user.mobile_user
        data = payload.dict()
        personal_info = PersonalInfo.objects.filter(mobile_user=mobile_user).first()
        if personal_info:
            raise ValidationException(_("You already have filled personal information."))
        personal_info = PersonalInfo.objects.create(**data, mobile_user=mobile_user)
        return personal_info
    else:
        raise ValidationException(_("User must be a mobile user."))


@transaction.atomic
def update_personal_info(user: User, payload: PersonalInfoUpdateSchema):
    if hasattr(user, 'mobile_user'):
        mobile_user = user.mobile_user
        data = payload.dict(exclude_unset=True)
        personal_info = get_object_or_404(PersonalInfo, mobile_user=mobile_user)
        for attr, value in data.items():
            setattr(personal_info, attr, value)

        personal_info.save()
        return personal_info
    else:
        raise ValidationException(_("User must be a mobile user."))


@transaction.atomic
def delete_personal_info(user: User):
    if hasattr(user, 'mobile_user'):
        mobile_user = user.mobile_user
        personal_info = get_object_or_404(PersonalInfo, mobile_user=mobile_user)
        if personal_info is None:
            raise
