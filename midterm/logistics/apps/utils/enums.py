from django.db.models import TextChoices


class UserType(TextChoices):
    WEB = 'web', 'web'
    MOBILE = 'mobile', 'mobile'


class RoleType(TextChoices):
    ADMIN = 'admin', 'admin'
    WAREHOUSE_MANAGER = 'warehouse_manager', 'warehouse_manager'
    PUP_MANAGER = 'pup_manager', 'pup_manager'


class CurrencyChoices(TextChoices):
    KZT = 'kzt', 'kzt'
    RUB = 'rub', 'rub'
    USD = 'usd', 'usd'
    CNY = 'cny', 'cny'


class OrderStatus(TextChoices):
    INTRODUCED = 'introduced', 'Введен'
    AT_WAREHOUSE = 'at_warehouse', 'На складе'
    ON_THE_WAY = 'on_the_way', 'В пути'
    AT_PICKUP_POINT = 'at_pickup_point', 'В ПВЗ'
    GIVEN = 'given', 'Получен'
    WAITING_FOR_PAYMENT = 'waiting_for_payment', 'Ожидает оплаты'
    PAID = 'paid', 'Оплачено'


class WarehouseType(TextChoices):
    DROPSHIPPING = 'Dropshipping', 'dropshipping'
    SORTING = 'Sorting', 'sorting'
    DISTRIBUTION = 'Distribution', 'distribution'


class JuridicalFrom(TextChoices):
    TOO = 'TOO', 'TOO'
    INDIVIDUAL_ENTREPRENEUR = 'ИП', 'ИП'


class PickUpPointStatus(TextChoices):
    INACTIVE = 'inactive', 'inactive'
    ACTIVE = 'active', 'active'
    IN_REVIEW = 'in_review', 'in_review'


class TransactionType(TextChoices):
    PAYMENT = 'payment', 'payment'
    DEPOSIT = 'deposit', 'deposit'
    WITHDRAWAL = 'withdrawal', 'withdrawal'


class TransactionStatus(TextChoices):
    FINISHED = 'finished', 'finished'
    PENDING = 'pending', 'pending'
    CANCELED = 'canceled', 'canceled'

    
class GenderType(TextChoices):
    MALE = 'male', 'male'
    FEMALE = 'female', 'female'


CURRENCY_CODES = {
    'usd': 480,
    'rub': 6,
    'kzt': 1,
}

WEIGHT_PRICE_COEFFICIENT = {
    'usd': 14,
    'rub': 1120,
    'kzt': 6720,
}
