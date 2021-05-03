import requests
from environs import Env
from pprint import pprint


def get_access_token(client_id, client_secret):
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    response = requests.post('https://api.moltin.com/oauth/access_token', data=data)
    response.raise_for_status()
    response = response.json()
    access_token = response['access_token']
    return access_token


def get_all_products(token):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get('https://api.moltin.com/v2/products', headers=headers)
    response.raise_for_status()
    response = response.json()
    return response['data']


def get_id_product(product):
    return product['id']


def add_product_to_cart(token, product_id, cart_name, quantity):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }

    data = {'data':
            {
                'id': product_id,
                'type': 'cart_item',
                'quantity': quantity
            }
           }

    response = requests.post(f'https://api.moltin.com/v2/carts/{cart_name}/items',
                             headers=headers,
                             json=data)
    response.raise_for_status()
    return response.json()


def get_cart(token, cart_name):
    headers = {
        'Authorization': f'Bearer {token}'
    }

    response = requests.get(f'https://api.moltin.com/v2/carts/{cart_name}', headers=headers)
    response.raise_for_status()
    return response.json()


def get_cart_items(token, cart_name):
    headers = {
        'Authorization': f'Bearer {token}',
    }

    response = requests.get(f'https://api.moltin.com/v2/carts/{cart_name}/items', headers=headers)
    response.raise_for_status()
    return response.json()


def main():
    env = Env()
    env.read_env()

    client_id = env('MULTIN_CLIENT_ID')
    client_secret = env('MULTIN_CLIENT_SECRET')

    access_token = get_access_token(client_id, client_secret)
    all_products = get_all_products(access_token)

    for product in all_products:
        product_id = get_id_product(product)
        # add_product = add_product_to_cart(access_token, product_id, '3456546', 2)
        # cart = get_cart(access_token, '3456546')
        # pprint(cart)
        pprint(get_cart_items(access_token, '34565464'))
        break


if __name__ == "__main__":
    main()