import requests
from environs import Env
from pprint import pprint


def get_access_token(url, client_id, client_secret):
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    response = response.json()
    access_token = response['access_token']
    token_type = response['token_type']
    return access_token, token_type


def get_all_products(url, token_type, token):
    headers = {'Authorization': f'{token_type} {token}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    response = response.json()
    return response['data']


def get_id_product(product):
    return product['id']


def get_cart(token_type, token, cart_name):
    headers = {
        'Authorization': f'{token_type} {token}',
    }

    response = requests.get(f'https://api.moltin.com/v2/carts/{cart_name}', headers=headers)
    response.raise_for_status()
    pprint(response.json())


def add_product_to_cart(token_type, token, product_id, cart_name):
    headers = {
        'Authorization': f'{token_type} {token}',
        'Content-Type': 'application/json',
    }

    data = {'data':
            {
                'id': product_id,
                'type': 'cart_item',
                'quantity': 1
            }
           }

    response = requests.post(f'https://api.moltin.com/v2/carts/{cart_name}/items', headers=headers, json=data)
    response.raise_for_status()
    pprint(response.json())


def main():
    env = Env()
    env.read_env()

    access_token_url = 'https://api.moltin.com/oauth/access_token'
    all_products_url = 'https://api.moltin.com/v2/products'

    client_id = env('MULTIN_CLIENT_ID')
    client_secret = env('MULTIN_CLIENT_SECRET')

    access_token, token_type = get_access_token(access_token_url, client_id, client_secret)
    all_products = get_all_products(all_products_url, token_type, access_token)

    for prosuct in all_products:
        product_id = get_id_product(prosuct)
        add_product_to_cart(token_type, access_token, product_id, '3456546')
        break


if __name__ == "__main__":
    main()