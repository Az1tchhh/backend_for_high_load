import os
import random
import string
from io import BytesIO

import barcode
from barcode.writer import ImageWriter


def upload_to(instance, prefix, filename):
    path = os.path.join(prefix, filename)
    return path


def generate_barcode(number):
    if not number:
        raise ValueError("Track number is required to generate a barcode.")

    barcode_class = barcode.get_barcode_class('code128')
    barcode_instance = barcode_class(number, writer=ImageWriter())

    barcode_image = BytesIO()
    barcode_instance.write(barcode_image)

    barcode_image.seek(0)
    barcode_response = barcode_image.getvalue()
    return barcode_response


def generate_order_barcode(code):
    if not code:
        raise ValueError("Code is required to generate a barcode.")

    barcode_class = barcode.get_barcode_class('code128')
    barcode_instance = barcode_class(code, writer=ImageWriter())

    options = {'write_text': False}

    buffer = BytesIO()
    barcode_instance.write(buffer, options=options)

    buffer.seek(0)
    barcode_response = buffer.getvalue()
    return barcode_response


def generate_unique_code(length=6):
    from apps.orders.models import OrderCode
    characters = string.digits
    while True:
        code = ''.join(random.choices(characters, k=length))
        if OrderCode.objects.filter(code=code).exists():
            continue
        return code


def convert_phone_number(phone_number: str):
    return f'+{phone_number[0]} {phone_number[1:4]} {phone_number[4:7]} {phone_number[7:9]} {phone_number[9:11]}'


def only_digits_phone_number(phone_number: str):
    return ''.join(phone_number for phone_number in phone_number if phone_number.isdigit())
