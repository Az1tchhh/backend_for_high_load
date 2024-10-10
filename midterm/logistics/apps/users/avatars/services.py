from apps.users.avatars.models import Avatar
from apps.utils.exceptions import ValidationException
from django.utils.translation import gettext_lazy as _


def create_avatar(data, image=None):
    avatar = Avatar.objects.create(**data, image=image)
    return avatar


def update_avatar(avatar_id, data, image):
    avatar = Avatar.objects.filter(id=avatar_id).first()

    if avatar is None:
        return ValidationException(_("Avatar not found"))

    for key, value in data.items():
        setattr(avatar, key, value)
    if image:
        avatar.image = image
    avatar.save()
    return avatar
