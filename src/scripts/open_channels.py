#!/usr/bin/env python
import threading
import typing
from typing import List

import click
import yaml

from raiden_api.api import Api
from raiden_api.model.exceptions import HttpErrorException
from raiden_api.model.requests import ManageChannelRequest, OpenChannelRequest


class NodeConfig:
    def __init__(self, address: str, port: int, funds: int, targets: List[str] = None):
        self.address = address
        self.port = port
        self.funds = funds
        self.targets = targets

    @classmethod
    def from_dict(cls, data: typing.Dict[str, typing.Any]) -> 'NodeConfig':

        targets: typing.Optional[List[str]] = None

        if 'targets' in data:
            targets = data['targets']

        response = cls(
            address=str(data['address']),
            port=int(data['port']),
            funds=int(data['funds']),
            targets=targets,
        )

        return response


class OpenJob(threading.Thread):
    def __init__(self, api: Api, node: NodeConfig, token_address: str):
        threading.Thread.__init__(self)
        self.__api = api
        self.__node = node
        self.__token_address = token_address

    def run(self):
        address_response = self.__api.address()
        address = address_response.our_address

        if self.__node.targets is None:
            print(f'Node {address} has no targets -- skipping')
            return

        for partner_address in self.__node.targets:

            try:
                request = OpenChannelRequest(
                    partner_address, self.__token_address, self.__node.funds
                )
                response = self.__api.open_channel(request)
                print(f'Successfully opened channel from {address} to {response.partner_address}')
            except HttpErrorException as e:
                print(f'error from {address} to {partner_address} [{str(e)}]')


@click.command()
@click.option('--token', required=True, type=str)
@click.option("--config", required=True, type=click.Path(exists=True, dir_okay=False))
def main(token: str, config: str):
    configuration_file = open(config, 'r')
    configuration = yaml.load(configuration_file)

    nodes_ = configuration['nodes']

    if not nodes_:
        print('nodes element is missing from configuration')
        exit(1)

    token_address = token

    nodes: List[NodeConfig] = list(map(lambda x: NodeConfig.from_dict(x), nodes_))
    apis: List[Api] = list(map(lambda x: Api(x.port), nodes))

    jobs = []

    number_of_nodes = len(nodes)
    for index in range(number_of_nodes):
        job = OpenJob(apis[index], nodes[index], token_address)
        jobs.append(job)
        job.start()

    for job in jobs:
        job.join()

    for index in range(number_of_nodes):
        node = nodes[index]
        api = apis[index]
        funds = node.funds

        all_channels = filter(lambda x: x.total_deposit == 0, api.channels())
        without_deposit = list(map(lambda x: x.partner_address, all_channels))

        print(f'funding {len(without_deposit)} channels for {node.port}')

        for no_funds_partner_address in without_deposit:
            try:
                deposit = ManageChannelRequest(total_deposit=funds)
                channel = api.manage_channel(deposit, token_address, no_funds_partner_address)
                print(f'new total_deposit: {channel.total_deposit} to {channel.partner_address}')
            except HttpErrorException as e:
                print(f'deposit to {no_funds_partner_address} failed {str(e)}')


if __name__ == '__main__':
    main()
