from django.db import models

from apps.country.models import City, Country
from apps.users.models import MobileUser


# Create your models here.
class MyAddress(models.Model):
    mobile_user = models.ForeignKey(MobileUser, on_delete=models.PROTECT, related_name='my_addresses')
    address_name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    address = models.CharField(max_length=100)


class PersonalInfo(models.Model):
    mobile_user = models.OneToOneField(MobileUser, on_delete=models.CASCADE, related_name='personal_info')
    document_number = models.CharField(max_length=9, unique=True)
    date_of_issue = models.DateField()
    validity_period = models.DateField()
    iin = models.CharField(max_length=12, unique=True)
    citizenship = models.ForeignKey(Country, on_delete=models.CASCADE)
    given_by = models.CharField(max_length=100)
