from ninja import Schema


class PaymentInitSchema(Schema):
    transaction_id: int


class PaymentWithSavedCard(Schema):
    card_token: str
    transaction_id: int
