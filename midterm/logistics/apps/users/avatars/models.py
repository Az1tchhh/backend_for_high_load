from django.db import models

from apps.utils.models import AbstractModel
from apps.utils.services import upload_to


def avatar_upload(instance, filename):
    return upload_to(instance, 'avatar', filename)


# Create your models here.
class Avatar(AbstractModel):
    name = models.CharField(max_length=50, null=False)
    image = models.ImageField(upload_to=avatar_upload, null=False)
