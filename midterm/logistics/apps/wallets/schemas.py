from typing import Optional

from ninja import Schema, ModelSchema
from pydantic import Field

from apps.users.schemas import MobileUserSchema
from apps.utils.enums import CurrencyChoices
from apps.wallets.models import Wallet, Transaction


class WalletCreateSchema(Schema):
    name: Optional[str] = None
    balance: float = 0


class WalletUpdateSchema(Schema):
    name: Optional[str] = None


class WalletRefillSchema(Schema):
    amount: float = Field(..., gt=0)
    currency: Optional[CurrencyChoices] = Field(CurrencyChoices.USD)


class WalletSchema(ModelSchema):
    mobile_user: MobileUserSchema = Field(..., alias='user.mobile_user')

    class Meta:
        model = Wallet
        fields = ('id', 'name', 'balance')


class TransactionSchema(ModelSchema):
    class Meta:
        model = Transaction
        fields = (
            'id',
            'amount',
            'wallet',
            'transaction_type',
            'status',
            'timestamp',
        )


class TransactionCreateSchema(Schema):
    amount: float = Field(..., gt=0)
