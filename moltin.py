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
    return response


def main():
    env = Env()
    env.read_env()

    access_token_url = 'https://api.moltin.com/oauth/access_token'
    all_products_url = 'https://api.moltin.com/v2/products'

    client_id = env('MULTIN_CLIENT_ID')
    client_secret = env('MULTIN_CLIENT_SECRET')
    access_token, token_type = get_access_token(access_token_url, client_id, client_secret)
    all_products = get_all_products(all_products_url, token_type, access_token)


if __name__ == "__main__":
    main()