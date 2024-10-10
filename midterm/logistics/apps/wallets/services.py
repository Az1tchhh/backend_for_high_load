from django.db import transaction
from django.utils.translation import gettext as _

from apps.orders.tasks import pay_orders_automatically
from apps.users.models import User
from apps.utils.enums import TransactionType, CurrencyChoices, CURRENCY_CODES
from apps.utils.exceptions import ValidationException
from apps.wallets.models import Wallet, Transaction
from apps.wallets.schemas import WalletCreateSchema, WalletRefillSchema


def get_my_wallet(user: User):
    wallet = Wallet.objects.filter(user=user).first()
    if wallet is None:
        raise ValidationException(_("You do not have a wallet yet."))
    return wallet


@transaction.atomic
def create_wallet(user: User, payload: WalletCreateSchema):
    wallet = Wallet.objects.filter(user=user).first()
    if wallet:
        raise ValidationException(_("Your wallet already exists."))
    data = payload.dict()
    wallet = Wallet.objects.create(**data, user=user)
    return wallet


@transaction.atomic
def refill_my_wallet(user: User, payload: WalletRefillSchema):
    wallet = get_my_wallet(user)
    data = payload.dict()
    amount = data.get('amount')
    currency = data.get('currency')
    if amount <= 0:
        raise ValidationException(_("The refill balance cannot be less than 0."))
    transaction = create_deposit_transaction(wallet, amount, currency)
    # pay_orders_automatically.apply_async(args=[user.id])
    return transaction


def finish_transaction(instance: Transaction) -> Transaction:
    if instance.transaction_type == TransactionType.DEPOSIT:
        wallet = Wallet.objects.get(id=instance.wallet.id)
        wallet.balance += instance.amount
        wallet.save()
        pay_orders_automatically.apply_async(args=[wallet.user.id])

    elif instance.transaction_type == TransactionType.WITHDRAWAL:
        wallet = Wallet.objects.get(id=instance.wallet.id)
        wallet.total_sum -= instance.amount
        wallet.save()

    return instance


@transaction.atomic
def create_deposit_transaction(wallet: Wallet, amount: int, currency: CurrencyChoices):
    if currency:
        amount = amount * CURRENCY_CODES[currency]

    transaction = Transaction.objects.create(
        wallet=wallet,
        amount=amount,
        transaction_type=TransactionType.DEPOSIT,
    )

    return transaction
