import logging

import requests
from environs import Env

logger = logging.getLogger('Продаём рыбку')


def get_products(auth_key, shop_url):
    headers = {'Authorization': f'Bearer {auth_key}'}

    response = requests.get(shop_url, headers=headers)
    response.raise_for_status()

    return response.json()


def get_token(user_id):
    data = {
        'client_id': user_id,
        'grant_type': 'implicit',}

    response = requests.post('https://api.moltin.com/oauth/access_token',
                             data=data)
    return response.json()

def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s')
    logger.setLevel(logging.DEBUG)

    env = Env()
    env.read_env()

    elasticpath_id = env.str('ELASTICPATH')
    elasticpath_url = 'https://api.moltin.com/v2/products'

    elasticpath_token = get_token(elasticpath_id)['access_token']
    products = get_products(elasticpath_token, elasticpath_url)
    print(products)


if __name__ == '__main__':
    main()