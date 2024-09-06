from django.db import models


class AbstractModel(models.Model):

    objects = models.Manager()

    class Meta:
        abstract = True
