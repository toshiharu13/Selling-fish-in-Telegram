import requests
from environs import Env


def get_products():
    data = {
        'client_id': 'XXXX',
        'grant_type': 'implicit',
    }

    response = requests.post('https://api.moltin.com/oauth/access_token', data=data)

    return response.json()


if __name__ == '__main__':
    ...