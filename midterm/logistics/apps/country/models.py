from django.db import models


# Create your models here.
class Country(models.Model):
    name = models.CharField(max_length=255, null=False)


class City(models.Model):
    country = models.ForeignKey(to=Country, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=255, null=False)
