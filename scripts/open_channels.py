#!/usr/bin/env python
import os

import click
import requests
import threading
import yaml

from raiden_api.api import Api


def open_channel(port: int, partner_address: str, token_address: str, funds: int):
    url = f'http://localhost:{port}/api/v1/channels'
    return requests.put(
        url,
        headers={'Content-Type': 'application/json', },
        json={
            'partner_address': partner_address,
            'token_address': token_address,
            'total_deposit': funds,
            "settle_timeout": 500
        },
        timeout=5 * 60
    )


def deposit(port: int, token_address: str, partner_address: str, funds: int):
    url = f'http://localhost:{port}/api/v1/channels/{token_address}/{partner_address}'
    return requests.patch(
        url,
        headers={'Content-Type': 'application/json', },
        json={
            'total_deposit': funds,
        },
        timeout=5 * 60
    ).status_code


def channels_without_deposit(port: int, token_address: str):
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
        if channel['total_deposit'] == 0:
            channels.append(channel['partner_address'])

    return channels


@click.command()
@click.option('--token', required=True, type=str)
@click.option("--config", required=True, type=click.Path(exists=True, dir_okay=False))
def main(token: str, config: os.path):
    configuration_file = open(config, 'r')
    configuration = yaml.load(configuration_file)

    nodes_ = configuration['nodes']

    if not nodes_:
        print('nodes element is missing from configuration')
        exit(1)

    token_address = token

    threads = []
    for target in nodes_:
        thread = threading.Thread(target=handle_opening, args=(target, token_address))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    for target in nodes_:
        port = target['port']
        funds = target['funds']

        without_deposit = channels_without_deposit(port, token_address)

        print(f'funding {len(without_deposit)} channels for {port}')

        for no_funds_partner_address in without_deposit:
            status = deposit(port, token_address, no_funds_partner_address, funds)
            if status != 200:
                print(f'deposit to {no_funds_partner_address} failed')
            else:
                print(f'added {funds} total_deposit to {no_funds_partner_address}')


def handle_opening(target, token_address: str):
    targets = target['targets'] if 'targets' in target else []
    port = target['port']
    funds = target['funds']

    api = Api(port)

    address = api.address()

    for partner_address in targets:
        response = open_channel(port, partner_address, token_address, funds)
        if response.status_code == 201:
            print(f'Successfully opened channels from {address.our_address} to {partner_address}')
        else:
            print(f'error from {target["address"]} to {partner_address} [{response.content}]')


if __name__ == '__main__':
    main()
