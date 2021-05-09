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
    headers = {'Authorization': f'Bearer {token}',
               'Content-Type': 'application/json'}

    data = {'data': {'id': product_id,
                     'type': 'cart_item',
                     'quantity': int(quantity)}}

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


def get_product(token, product_id):
    headers = {
        'Authorization': f'Bearer {token}',
    }

    response = requests.get(f'https://api.moltin.com/v2/products/{product_id}', headers=headers)
    response.raise_for_status()
    return response.json()


def get_image_url(token, file_id):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(f'https://api.moltin.com/v2/files/{file_id}', headers=headers)
    response.raise_for_status()
    return response.json()['data']['link']['href']


def delete_product_in_cart(token, cart_name, product_id):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.delete(f'https://api.moltin.com/v2/carts/{cart_name}/items/{product_id}', headers=headers)
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
        add_product = add_product_to_cart(access_token, product_id, 'b34t', 1)
        pprint(add_product)
        print('======================')
        cart = get_cart(access_token, 'b34t')
        pprint(cart)
        print('======================')
        pprint(get_cart_items(access_token, 'b34t'))
        break


if __name__ == "__main__":
    main()