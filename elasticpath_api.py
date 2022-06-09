import os
import time

import requests

TOKEN_EXPIRES = 0
SHOP_TOKEN = ''


def get_credentials():
    auth_key = get_token()
    return {'Authorization': f'Bearer {auth_key}'}


def get_products():
    headers = get_credentials()
    url = 'https://api.moltin.com/v2/products'

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    decoded_response = response.json()
    if 'error' in decoded_response:
        raise requests.exceptions.HTTPError(decoded_response['error'])
    return decoded_response


def get_product_by_id(prod_id):
    headers = get_credentials()
    url = f'https://api.moltin.com/v2/products/{prod_id}'

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    decoded_response = response.json()
    if 'error' in decoded_response:
        raise requests.exceptions.HTTPError(decoded_response['error'])
    return decoded_response


def get_image_by_id(img_id):
    headers = get_credentials()
    url = f'https://api.moltin.com/v2/files/{img_id}'

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    decoded_response = response.json()
    if 'error' in decoded_response:
        raise requests.exceptions.HTTPError(decoded_response['error'])
    img = decoded_response['data']['link']['href']
    return img


def get_token():
    elasticpath_id = os.environ['ELASTICPATH_CLIENT_ID']
    global TOKEN_EXPIRES, SHOP_TOKEN
    data = {
        'client_id': elasticpath_id,
        'grant_type': 'implicit'}
    if time.time() > TOKEN_EXPIRES:
        response = requests.post('https://api.moltin.com/oauth/access_token',
                                 data=data)
        response.raise_for_status()
        decoded_response = response.json()
        if 'error' in decoded_response:
            raise requests.exceptions.HTTPError(decoded_response['error'])

        TOKEN_EXPIRES = decoded_response['expires']
        SHOP_TOKEN = decoded_response['access_token']
    return SHOP_TOKEN


def add_product_to_cart(product_id, quantity, cart_id='card_id'):
    payload = {
        'data': {
            'id': product_id,
            'type': 'cart_item',
            'quantity': quantity}}
    headers = get_credentials()

    url = f'https://api.moltin.com/v2/carts/{cart_id}/items'
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    decoded_response = response.json()
    if 'error' in decoded_response:
        raise requests.exceptions.HTTPError(decoded_response['error'])
    return decoded_response


def get_products_in_cart(card_id):
    headers = get_credentials()
    url = f'https://api.moltin.com/v2/carts/{card_id}/items'

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    decoded_response = response.json()
    if 'error' in decoded_response:
        raise requests.exceptions.HTTPError(decoded_response['error'])
    return decoded_response


def get_cart_total(cart_id):
    headers = get_credentials()
    url = f"https://api.moltin.com/v2/carts/{cart_id}"

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    decoded_response = response.json()
    if 'error' in decoded_response:
        raise requests.exceptions.HTTPError(decoded_response['error'])
    return decoded_response


def remove_cart_item(cart_id, product_id):
    headers = get_credentials()
    url = f"https://api.moltin.com/v2/carts/{cart_id}/items/{product_id}"

    response = requests.delete(url, headers=headers)
    response.raise_for_status()
    decoded_response = response.json()
    if 'error' in decoded_response:
        raise requests.exceptions.HTTPError(decoded_response['error'])
    return decoded_response


def create_customer(user_name, user_email):
    headers = get_credentials()
    url = "https://api.moltin.com/v2/customers"
    payload = {
        "data": {
            "type": "customer",
            "name": user_name,
            "email": user_email}}

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    decoded_response = response.json()
    if 'error' in decoded_response:
        raise requests.exceptions.HTTPError(decoded_response['error'])
    return decoded_response
