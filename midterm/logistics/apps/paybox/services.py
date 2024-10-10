import base64
import hashlib
import secrets
from urllib.parse import parse_qs

import requests
import xml.etree.ElementTree as ET

from collections import OrderedDict
from apps.utils.enums import TransactionStatus
from apps.utils.exceptions import ValidationException
from apps.utils.services import convert_phone_number, only_digits_phone_number
from apps.wallets.models import Transaction
from apps.wallets.services import finish_transaction
from config.settings import env

secret_key_accepting = env('SECRET_KEY_FOR_ACCEPTING')
merchant_id = env('MERCHANT_ID')
paybox_base_url = env('PAYBOX_BASE_URL')


def generate_sign(data, sign_type):
    data = OrderedDict(sorted(data.items()))
    new_data = OrderedDict([(0, f'{sign_type}')] + list(data.items()) + [(1, secret_key_accepting)])
    return hashlib.md5(';'.join(str(i) for i in new_data.values()).encode('utf-8')).hexdigest()


def generate_salt(length=16):
    salt_bytes = secrets.token_bytes(length)
    salt_base64 = base64.b64encode(salt_bytes).decode('utf-8')
    return salt_base64


salt = generate_salt()


def start_init_payment(transaction_id):
    url = f'{paybox_base_url}/init_payment.php'
    transaction = Transaction.objects.get(id=transaction_id)
    phone_number = only_digits_phone_number(transaction.wallet.user.mobile_user.phone_number)
    data = {
        'pg_order_id': transaction.id,
        'pg_salt': salt,
        'pg_merchant_id': merchant_id,
        'pg_amount': transaction.amount,
        'pg_description': f'Перевод денег: {phone_number}',
        'pg_currency': 'KZT',
        'pg_language': 'ru',
        'pg_testing_mode': '1',
        'pg_success_url': 'http://2.135.67.66/api/paybox/result/success/',
        'pg_failure_url': 'http://2.135.67.66/api/paybox/result/failure/',
        'pg_result_url': 'http://2.135.67.66/api/paybox/result/payment/',  # 8001 port for testing
        'pg_user_phone': f'{phone_number}',
        'pg_user_id': f'{transaction.wallet.user.id}'
    }
    data['pg_sig'] = generate_sign(data, 'init_payment.php')
    response = requests.post(url, data=data)
    xml_text = ET.fromstring(response.text)
    try:
        message = xml_text.find('pg_redirect_url').text, 200
    except Exception as e:
        message = xml_text.find('pg_error_description').text, 400
    return message


def process_response(response):
    print('process_response function prints:')
    print(response)
    print(type(response))

    parsed_data = parse_qs(response)
    pg_result = int(parsed_data.get('pg_result', [None])[0])
    transaction_id = int(parsed_data.get('pg_order_id', [None])[0])

    transaction = Transaction.objects.get(id=transaction_id)
    if pg_result == 1:
        if transaction.status == TransactionStatus.PENDING:
            transaction.status = TransactionStatus.FINISHED
            transaction.save()
            finish_transaction(transaction)
    else:
        transaction.status = TransactionStatus.CANCELED
        transaction.save()
