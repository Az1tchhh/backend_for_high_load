from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from assignment_1.apps.users.managers import UserManager
from assignment_1.apps.utils.models import AbstractModel


# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True)
    is_blog_user = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'


class BlogUser(AbstractModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='blog_user')
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=10, unique=True, null=True, blank=True)
