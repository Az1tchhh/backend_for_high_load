from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from apps.users.avatars.models import Avatar
from apps.users.managers import UserManager
from apps.utils.enums import RoleType, GenderType
from apps.utils.models import AbstractModel
from apps.utils.services import upload_to


def profile_photo_upload(instance, filename):
    return upload_to(instance, 'profile_photos', filename)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True)
    is_web_user = models.BooleanField(default=False)
    is_mobile_user = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'


# Create your models here.
class MobileUser(AbstractModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mobile_user')
    profile_photo = models.ImageField(upload_to=profile_photo_upload, null=True, blank=True)
    avatar = models.ForeignKey(Avatar, on_delete=models.CASCADE, null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    gender = models.CharField(choices=GenderType.choices, max_length=15, blank=True, null=True)


class WebUser(AbstractModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='web_user')
    phone_number = models.CharField(max_length=15, unique=True)
    role = models.CharField(choices=RoleType.choices, blank=True, null=True, max_length=100)


class WebUserAssignment(models.Model):
    web_user = models.OneToOneField(to='users.WebUser', on_delete=models.CASCADE, related_name='assignment')
    warehouse = models.OneToOneField(to='warehouse.Warehouse', on_delete=models.SET_NULL, null=True, blank=True)
    pickup_point = models.OneToOneField(to='pickup_point.PickUpPoint', on_delete=models.SET_NULL, null=True, blank=True)
