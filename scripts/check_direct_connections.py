#!/usr/bin/env python
import time

import click
import requests

from raiden_api.api import Api


def direct_partners(port: int, token_address: str):
    url = f'http://localhost:{port}/api/v1/channels'
    response = requests.get(
        url,
        headers={'Content-Type': 'application/json', },
        timeout=5 * 60
    )

    if response.status_code != 200:
        print(f'Could not get channels for {token_address} [{response.status_code}]')
        return

    channels_response = response.json()

    channels = []

    for channel in channels_response:
        channels.append(channel['partner_address'])

    return channels


def transfer(port: int, token: str, partner_address: str):
    url = f'http://localhost:{port}/api/v1/payments/{token}/{partner_address}'
    return requests.post(
        url,
        headers={'Content-Type': 'application/json', },
        json={'amount': 1, 'identifier': time.time()},
        timeout=60
    )


@click.command()
@click.option('--token', required=True, type=str)
@click.option('--start-port', required=True, type=int)
@click.option('--end-port', required=True, type=int)
def main(token: str, start_port: int, end_port: int):
    for port in range(start_port, end_port):
        partners = direct_partners(port, token)

        api = Api(port)

        address_response = api.address()
        our_address = address_response.our_address

        for partner_address in partners:

            try:
                response = transfer(port, token, partner_address)
                if response.status_code == 200:
                    print(f'{our_address} to {partner_address} [v]')
                else:
                    print(f'{our_address} to {partner_address} [x]')
            except requests.exceptions.RequestException:
                print(f'{our_address} to {partner_address} [x]')
                pass


if __name__ == '__main__':
    main()
