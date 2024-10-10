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
        'pg_success_url': 'http://2.135.67.66:8001/api/paybox/result/success/',
        'pg_failure_url': 'http://2.135.67.66:8001/api/paybox/result/failure/',
        'pg_result_url': 'http://2.135.67.66:8001/api/paybox/result/payment/',  # 8001 port for testing
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


def pay_with_saved_card(card_token, transaction_id):
    transaction = Transaction.objects.filter(id=transaction_id).first()
    if transaction is None:
        raise ValidationException('Transaction not found')
    first_step_url = f'{paybox_base_url}/v1/merchant/{merchant_id}/card/init'
    phone_number = convert_phone_number(transaction.wallet.user.mobile_user.phone_number)

    first_step_post_data = {
        'pg_merchant_id': merchant_id,
        'pg_user_id': transaction.wallet.user.id,
        'pg_amount': transaction.amount,
        'pg_order_id': transaction.id,
        'pg_description': f'Перевод денег: {phone_number}',
        'pg_card_token': card_token,
        'pg_result_url': 'http://2.135.67.66:8001/api/paybox/result/payment/',
        'pg_success_url': 'http://2.135.67.66:8001/api/paybox/result/success/',
        'pg_failure_url': 'http://2.135.67.66:8001/api/paybox/result/failure/',
        'pg_salt': salt,
    }
    first_step_post_data['pg_sig'] = generate_sign(first_step_post_data, 'init')
    first_step_response = requests.post(first_step_url, first_step_post_data)
    first_step_xml_text = ET.fromstring(first_step_response.text)

    pg_status = first_step_xml_text.find('pg_status').text
    if pg_status != 'ok':
        raise ValidationException('Payment status returned error')

    pg_payment_id = first_step_xml_text.find('pg_payment_id').text
    pg_salt = first_step_xml_text.find('pg_salt').text

    second_step_url = f'{paybox_base_url}/v1/merchant/{merchant_id}/card/pay'

    second_step_post_data = {
        'pg_merchant_id': merchant_id,
        'pg_payment_id': pg_payment_id,
        'pg_salt': pg_salt,
    }
    second_step_post_data['pg_sig'] = generate_sign(second_step_post_data, 'pay')
    second_step_response = requests.post(second_step_url, second_step_post_data)
    return second_step_response.text


def save_user_card(user):
    url = f'{paybox_base_url}/v1/merchant/{merchant_id}/cardstorage/add2'
    data = {
        'pg_merchant_id': merchant_id,
        'pg_user_id': user.id,
        'pg_salt': salt,
        'pg_post_link': 'http://2.135.67.66:8001/api/paybox/result/card-save/',
        'pg_back_link': 'http://2.135.67.66:8001/'
    }
    data['pg_sig'] = generate_sign(data, 'add2')

    response = requests.post(url, data=data)

    xml_text = ET.fromstring(response.text)
    try:
        message = xml_text.find('pg_redirect_url').text, 200
    except Exception as e:
        message = xml_text.find('pg_error_description').text, 400
    return message


def get_user_cards(user):
    card_list = []
    url = f'{paybox_base_url}/v1/merchant/{merchant_id}/cardstorage/list'
    data = {
        'pg_merchant_id': merchant_id,
        'pg_user_id': user.id,
        'pg_salt': salt
    }

    data['pg_sig'] = generate_sign(data, 'list')

    response = requests.post(url, data=data)
    if response.status_code == 200:
        xml_text = ET.fromstring(response.text)
        for card in xml_text.findall('card'):
            card_json = {
                'card_id': card.find('pg_card_id').text,
                'card_hash': card.find('pg_card_hash').text,
                'card_token': card.find('pg_card_token').text,
                'card_status': card.find('pg_status').text
            }
            card_list.append(card_json)

    return card_list


def delete_user_card(user, card_token):
    url = f'{paybox_base_url}/v1/merchant/{merchant_id}/cardstorage/remove'
    data = {
        'pg_merchant_id': merchant_id,
        'pg_user_id': user.id,
        'pg_card_token': card_token,
        'pg_salt': salt
    }

    data['pg_sig'] = generate_sign(data, 'remove')

    response = requests.post(url, data=data)

    message = 'something wrong', 400
    if response.status_code == 200:
        xml_text = ET.fromstring(response.text)
        card = xml_text.find('card')
        message = card.find('pg_status').text
        return message, 200

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

# def process_withdrawal_response(response):
#     transaction_id = int(response['pg_order_id'][0])
#     pg_status = response['pg_status'][0]
#     # pg_card_hash = response['pg_card_hash'][0]
#
#     transaction = Transaction.objects.get(id=transaction_id)
#
#     if pg_status == 'ok':
#         transaction.status = TransactionStatus.FINISHED
#         transaction.save()
#
#     else:
#         transaction.status = TransactionStatus.CANCELED
#         transaction.save()


# def withdrawal(transaction_sum, user):
#     if abs(transaction_sum) > user.wallet.total_sum:
#         return 'Недостаточно средств', 400
#     url = f'{paybox_base_url}/api/reg2nonreg'
#
#     now_datetime = datetime.now() + timedelta(hours=1)
#
#     transaction = Transaction.objects.create(
#         wallet=user.wallet,
#         transaction_type=TransactionType.WITHDRAWAL,
#         sum=transaction_sum
#     )
#     phone_number = convert_phone_number(user.mobile_user.phone_number)
#     data = {
#         'pg_merchant_id': merchant_id,
#         'pg_amount': transaction_sum,
#         'pg_order_id': transaction.id,
#         'pg_description': f'Вывод денег: {phone_number}',
#         'pg_post_link': 'http://77.243.80.132/api/paybox/withdrawal/result/',
#         'pg_back_link': 'https://youtube.com',
#         'pg_order_time_limit': now_datetime.strftime('%Y-%m-%d %H:%M:%S'),
#         'pg_salt': salt,
#     }
#
#     new_data = generate_data_with_sign(data, 'reg2nonreg')
#     response = requests.post(url, new_data)
#     xml_text = ET.fromstring(response.text)
#
#     try:
#         message = xml_text.find('pg_redirect_url').text, 200
#     except:
#         message = xml_text.find('pg_status').text, 400
#
#     return message
#
#
# def withdrawal_with_saved_card(card_id, transaction_sum, user):
#     url = f'{paybox_base_url}/api/reg2reg'
#
#     now_datetime = datetime.now() + timedelta(hours=1)
#     phone_number = convert_phone_number(user.mobile_user.phone_number)
#
#     transaction = Transaction.objects.create(
#         wallet=user.wallet,
#         transaction_type=TransactionType.WITHDRAWAL,
#         sum=-abs(transaction_sum)
#     )
#
#     data = {
#         'pg_merchant_id': merchant_id,
#         'pg_amount': transaction_sum,
#         'pg_order_id': transaction.id,
#         'pg_card_id_to': card_id,
#         'pg_description': f'Перевод денег: {phone_number}',
#         'pg_post_link': 'http://77.243.80.132/api/paybox/withdrawal/result/',
#         'pg_back_link': 'https://youtube.com',
#         'pg_order_time_limit': now_datetime.strftime('%Y-%m-%d %H:%M:%S'),
#         'pg_salt': salt,
#     }
#
#     new_data = generate_data_with_sign(data, 'reg2reg')
#     response = requests.post(url, new_data)
#     xml_text = ET.fromstring(response.text)
#
#     message = xml_text.find('pg_status').text
#
#     return message
