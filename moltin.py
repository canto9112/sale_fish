import requests


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


def create_customer(token, name, email):
    headers = {'Authorization': f'Bearer {token}',
               'Content-Type': 'application/json'}

    data = {'data': {
                "type": "customer",
                "name": name,
                "email": email}}

    response = requests.post('https://api.moltin.com/v2/customers', headers=headers, json=data)
    response.raise_for_status()
    return response.json()
