from ninja_extra import api_controller, ControllerBase, route

from apps.users.permissions import IsMobileUser
from apps.wallets.models import Transaction
from apps.wallets.schemas import WalletSchema, WalletUpdateSchema, WalletRefillSchema, \
    TransactionSchema
from apps.wallets.services import get_my_wallet, refill_my_wallet


@api_controller('mobile/wallets/', permissions=[IsMobileUser], tags=['mobile-wallets'])
class WalletController(ControllerBase):

    @route.get('my/', response=WalletSchema)
    def my_wallets(self):
        user = self.context.request.auth
        my_wallet = get_my_wallet(user)
        return my_wallet

    @route.patch('', response=WalletSchema)
    def update_wallet(self, payload: WalletUpdateSchema):
        user = self.context.request.auth
        wallet = get_my_wallet(user)
        wallet.name = payload.name
        wallet.save()
        return wallet

    @route.post('refill/', response=TransactionSchema)
    def refill_wallet(self, payload: WalletRefillSchema):
        user = self.context.request.auth
        wallet = refill_my_wallet(user, payload)
        return wallet


@api_controller('transactions/', permissions=[IsMobileUser], tags=['transactions'])
class TransactionController(ControllerBase):

    def get_queryset(self):
        queryset = Transaction.objects.all()
        user = self.context.request.auth
        if user.is_web_user:
            pass
        elif user.is_mobile_user:
            wallet = get_my_wallet(user)
            queryset = queryset.filter(wallet=wallet)

        return queryset

    @route.get('', response=list[TransactionSchema])
    def transactions(self):
        queryset = self.get_queryset()
        return queryset
