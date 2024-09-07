from django.db import models

from apps.utils.models import AbstractModel, TimeStampMixin


# Create your models here.
class Post(AbstractModel, TimeStampMixin):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.CharField(max_length=255)

    def __str__(self):
        return self.title
