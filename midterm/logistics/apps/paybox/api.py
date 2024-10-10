from ninja.responses import Response
from ninja_extra import api_controller, ControllerBase, route, status

from apps.paybox.schemas import PaymentInitSchema, PaymentWithSavedCard
from apps.paybox.services import start_init_payment, process_response
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


@api_controller('paybox/result/', auth=None)
class PayboxResultController(ControllerBase):
    @route.post('payment/')
    def payment_result(self, request):
        response = self.context.request.body
        response = response.decode('utf-8')
        process_response(response)
        return Response({'message': 'OK'})

    @route.post('success/')
    def success(self, request):
        return Response({'message': 'OK'}, status=status.HTTP_200_OK)

    @route.post('failure/')
    def failure(self, request):
        return Response({'message': 'FAIL'}, status=status.HTTP_400_BAD_REQUEST)