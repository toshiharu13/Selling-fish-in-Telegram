import logging
import time
import requests
from environs import Env
import os

TOKEN_EXPIRES = 0
SHOP_TOKEN = ''
logger = logging.getLogger('Продаём рыбку')


def get_products():
    auth_key = get_token()
    headers = {'Authorization': f'Bearer {auth_key}'}
    url = 'https://api.moltin.com/v2/products'

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_product_by_id(prod_id):
    auth_key = get_token()
    headers = {'Authorization': f'Bearer {auth_key}'}
    url = f'https://api.moltin.com/v2/products/{prod_id}'

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_image_by_id(img_id):
    auth_key = get_token()
    headers = {'Authorization': f'Bearer {auth_key}'}
    url = f'https://api.moltin.com/v2/files/{img_id}'

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    img = response.json()['data']['link']['href']
    return img


def get_token():
    elasticpath_id = os.environ['ELASTICPATH']
    global TOKEN_EXPIRES, SHOP_TOKEN
    data = {
        'client_id': elasticpath_id,
        'grant_type': 'implicit'}
    if time.time() > TOKEN_EXPIRES:
        response = requests.post('https://api.moltin.com/oauth/access_token',
                                 data=data).json()
        TOKEN_EXPIRES = response['expires']
        SHOP_TOKEN = response['access_token']
    return SHOP_TOKEN


def add_product_to_cart(product_id, quantity, cart_id='card_id'):
    auth_key = get_token()
    payload = {
        'data': {
            'id': product_id,
            'type': 'cart_item',
            'quantity': quantity}}
    headers = {'Authorization': f'Bearer {auth_key}'}
    url = f'https://api.moltin.com/v2/carts/{cart_id}/items'
    response = requests.post(url, headers=headers, json=payload)
    return response.json()


def get_products_in_cart(card_id):
    auth_key = get_token()
    headers = {'Authorization': f'Bearer {auth_key}',}
    url = f'https://api.moltin.com/v2/carts/{card_id}/items'

    response = requests.get(url, headers=headers)
    return response.json()


def get_cart_total(cart_id):
    auth_key = get_token()
    headers = {'Authorization': f'Bearer {auth_key}',}
    url = f"https://api.moltin.com/v2/carts/{cart_id}"

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()


def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s')
    logger.setLevel(logging.DEBUG)

    env = Env()
    env.read_env()


if __name__ == '__main__':
    main()
