from django.db import models

from apps.utils.enums import PickUpPointStatus, JuridicalFrom
from apps.utils.services import upload_to


def individual_identification_number_upload(instance, filename):
    return upload_to(instance, 'individual_identification_number', filename)


def online_banking_certificate_upload(instance, filename):
    return upload_to(instance, 'online_banking_certificate', filename)


def nds_payer_certificate_upload(instance, filename):
    return upload_to(instance, 'nds_payer_certificate', filename)


# Create your models here.

class PickUpPoint(models.Model):
    city = models.ForeignKey(to='country.City', on_delete=models.CASCADE, null=False)
    address = models.CharField(max_length=255, null=False)
    name = models.CharField(max_length=255, null=False)
    phone_number = models.CharField(max_length=15, null=False)
    email = models.EmailField(null=True)
    full_name = models.CharField(max_length=255, null=False)
    juridical_form = models.CharField(max_length=20, null=False, choices=JuridicalFrom.choices)
    individual_identification_number = models.FileField(upload_to=individual_identification_number_upload, null=False)
    online_banking_certificate = models.FileField(upload_to=online_banking_certificate_upload, null=False)
    nds_payer = models.BooleanField(null=False)
    nds_payer_certificate = models.FileField(upload_to=nds_payer_certificate_upload, null=True)
    cells_in_stock = models.IntegerField(null=False)
    status = models.CharField(null=False, choices=PickUpPointStatus.choices, default=PickUpPointStatus.INACTIVE)


class Cell(models.Model):
    pickup_point = models.ForeignKey(to='pickup_point.PickUpPoint', on_delete=models.CASCADE, null=True, blank=True,
                                     related_name='cells')
    user = models.ForeignKey(to='users.MobileUser', on_delete=models.SET_NULL, null=True, blank=True)
    is_full = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    cell_number = models.PositiveIntegerField(null=False)
    max_orders = models.IntegerField(null=False)

    def __str__(self):
        location = self.pickup_point.name
        return f"Cell in {location} for User {self.user}" if self.user else f"Unassigned Cell in {location}"