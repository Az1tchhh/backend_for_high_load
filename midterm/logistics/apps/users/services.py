from django.contrib.auth.hashers import make_password, check_password
from django.utils.translation import gettext as _
from ninja_jwt.tokens import RefreshToken

from apps.users.models import User, MobileUser
from apps.utils.exceptions import ValidationException


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def change_password(user: User, passwords):
    current_password = passwords.get('current_password')
    new_password = passwords.get('new_password')
    if current_password == new_password:
        raise ValidationException(_("The new password must be different from the old one."))
    if not check_password(current_password, user.password):
        raise ValidationException(_("The old password is incorrect."))
    user.password = make_password(new_password)
    user.save()
    return


def update_mobile_user(obj, data):
    phone_number = data.get('phone_number', None)
    mobile_user = MobileUser.objects.filter(phone_number=phone_number).first()
    if mobile_user:
        raise ValidationException(_("The phone number is already registered in the system."))
    for attr, value in data.items():
        setattr(obj, attr, value)
    obj.save()
