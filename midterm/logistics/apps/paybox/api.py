from ninja.responses import Response
from ninja_extra import api_controller, ControllerBase, route, status

from apps.paybox.schemas import PaymentInitSchema, PaymentWithSavedCard
from apps.paybox.services import start_init_payment, save_user_card, get_user_cards, delete_user_card, process_response, \
    pay_with_saved_card
from apps.users.permissions import IsMobileUser


@api_controller('paybox/', permissions=[IsMobileUser])
class PayboxController(ControllerBase):

    @route.post('payment/init-payment/')
    def init_payment(self, payload: PaymentInitSchema):
        data = payload.dict()
        transaction_id = data.get('transaction_id')
        message, status_code = start_init_payment(transaction_id)
        if status_code == 400:
            status_code = status.HTTP_400_BAD_REQUEST
        else:
            status_code = status.HTTP_200_OK
        return Response({'message': message}, status=status_code)

    @route.post('pay-with-saved-card/')
    def pay_with_saved_card(self, payload: PaymentWithSavedCard):
        data = payload.dict()
        transaction_id = data.get('transaction_id')
        card_token = data.get('card_token')
        message = pay_with_saved_card(card_token, transaction_id)
        return message

    @route.post('card-save/')
    def card_save(self):
        message, status_code = save_user_card(self.context.request.auth)

        if status_code == 400:
            status_code = status.HTTP_400_BAD_REQUEST
        else:
            status_code = status.HTTP_200_OK
        return Response({'message': message}, status=status_code)

    @route.get('card-list/')
    def card_list(self, request):
        return Response({'message': get_user_cards(self.context.request.auth)})

    @route.delete('card-delete/<str:card_token>/')
    def card_delete(self, card_token: str):
        message, status_code = delete_user_card(self.context.request.auth, card_token)

        if status_code == 400:
            status_code = status.HTTP_400_BAD_REQUEST
        else:
            status_code = status.HTTP_200_OK
        return Response({'message': message}, status=status_code)

    # @route.post('withdrawal/')
    # def withdrawal(self, payload: WithdrawalCreateSchema):
    #     data = payload.dict(exclude_unset=True)
    #
    #     message, status_code = withdrawal(data.get('transaction_sum'), self.context.request.auth)
    #     if status_code == 400:
    #         status_code = status.HTTP_400_BAD_REQUEST
    #     else:
    #         status_code = status.HTTP_200_OK
    #     return Response({'message': message}, status=status_code)
    #
    # @route.post('withdrawal/saved-card/')
    # def withdrawal_saved_card(self, payload: WithdrawalCreateSchema):
    #     data = payload.dict(exclude_unset=True)
    #     card_id = data.get('card_id')
    #     transaction_sum = data.get('transaction_sum')
    #     user = self.context.request.auth
    #     if user.wallet.total_sum > abs(transaction_sum):
    #         message = withdrawal_with_saved_card(
    #             card_id,
    #             transaction_sum,
    #             user
    #         )
    #         return Response({'message': f'{message}'})
    #     return Response({'message': 'Недостаточно средств'}, status=status.HTTP_400_BAD_REQUEST)

    # @route.post('withdrawal/result/')
    # def withdrawal_result(self, request):
    #     response = request.data
    #     process_withdrawal_response(response)
    #     return Response({'message': 'OK'})


@api_controller('paybox/result/', auth=None)
class PayboxResultController(ControllerBase):
    @route.post('payment/')
    def payment_result(self, request):
        response = self.context.request.body
        response = response.decode('utf-8')
        process_response(response)
        return Response({'message': 'OK'})

    @route.post('card-save/')
    def card_save_result(self, request):
        response = request.data
        print(response)
        return Response({'message': 'OK'})

    @route.post('success/')
    def success(self, request):
        return Response({'message': 'OK'}, status=status.HTTP_200_OK)

    @route.post('failure/')
    def failure(self, request):
        return Response({'message': 'FAIL'}, status=status.HTTP_400_BAD_REQUEST)