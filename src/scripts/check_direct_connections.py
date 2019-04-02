#!/usr/bin/env python
import time

import click
import requests

from raiden_api.api import Api
from raiden_api.model.requests import PaymentRequest


@click.command()
@click.option('--token', required=True, type=str)
@click.option('--start-port', required=True, type=int)
@click.option('--end-port', required=True, type=int)
def main(token: str, start_port: int, end_port: int):
    for port in range(start_port, end_port):

        api = Api(port)

        address_response = api.address()
        our_address = address_response.our_address

        channels = api.channels()

        for channel in channels:
            partner_address = channel.partner_address

            try:
                payment_request = PaymentRequest(amount=1, identifier=int(time.time()))
                payment_response = api.payment(
                    receiver=partner_address, request=payment_request, token=token
                )
                print(f'{our_address} to {partner_address} [v] -- ({payment_response.identifier})')
            except requests.exceptions.RequestException:
                print(f'{our_address} to {partner_address} [x]')
                pass


if __name__ == '__main__':
    main()
