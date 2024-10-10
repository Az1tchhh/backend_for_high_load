from django.db import models

from apps.users.models import User
from apps.utils.enums import TransactionType, TransactionStatus


# Create your models here.
class Wallet(models.Model):
    name = models.CharField(max_length=255, default='')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=0)


class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(choices=TransactionType.choices, max_length=50)
    status = models.CharField(
        choices=TransactionStatus.choices,
        default=TransactionStatus.PENDING
    )
    timestamp = models.DateTimeField(auto_now_add=True)
