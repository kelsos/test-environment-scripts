#!/usr/bin/env python

import signal
import subprocess
import sys
import threading
import time
from typing import List

import click
from web3 import HTTPProvider, Web3

WEI_TO_ETH = 10 ** 18


class ServiceExit(Exception):
    pass


class MineJob(threading.Thread):
    def __init__(self, web3: Web3, sender: str, receiver: str, block_time: int):
        threading.Thread.__init__(self)
        self.terminate = threading.Event()
        self.web3 = web3
        self.sender = sender
        self.receiver = receiver
        self.block_time = block_time

    def run(self):
        while not self.terminate.is_set():
            time.sleep(self.block_time)
            try:
                send(self.web3, self.sender, self.receiver, 1)
            except ConnectionError as err:
                print(f'Connection failed {err}')


def start_parity():
    cmd = "parity --chain dev --reseal-min-period=0 --jsonrpc-apis all --jsonrpc-cors all"
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)


def service_shutdown(signum, frame):
    print(f'Caught signal {signum}')
    raise ServiceExit


def send(web3: Web3, sender: str, receiver: str, wei_value: int):
    unlock_account(sender, web3)
    transaction = web3.eth.sendTransaction({'to': receiver, 'from': sender, 'value': wei_value})
    print(transaction)
    print(f'{receiver} has a balance of {web3.eth.getBalance(receiver)}')


def unlock_account(address: str, web3: Web3):
    if not web3.personal.unlockAccount(address, ''):
        print('Failed to unlock prefunded')
        sys.exit(1)


@click.command()
@click.option("--rpc-url", default="http://localhost:8545")
@click.option('--accounts', envvar="RT_ENV__TESTING_ACCOUNTS", required=True)
@click.option('--block-time', type=int, default=1)
def main(rpc_url: str, accounts: str, block_time):
    testing_accounts = accounts.split(':')
    web3 = Web3(HTTPProvider(rpc_url))
    sender = web3.toChecksumAddress('0x00a329c0648769a73afac7f9381e08fb43dbea72')

    eth = 20 * WEI_TO_ETH

    try:
        chain = start_parity()
        print(f'started parity with {chain.pid}')
        time.sleep(10)

        fund_accounts(web3, sender, testing_accounts, eth)

        job = MineJob(web3, sender, testing_accounts[0], block_time)
        job.start()

        while True:
            time.sleep(1)

    except ServiceExit:
        job.terminate.set()
        job.join()
        chain.terminate()


def fund_accounts(web3: Web3, sender: str, testing_accounts: List[str], eth: int):
    print(f'preparing to fund accounts: {testing_accounts}')
    for receiver in testing_accounts:
        balance = web3.eth.getBalance(receiver)
        if balance > 0:
            continue

        send(web3, sender, receiver, eth)


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, service_shutdown)
    signal.signal(signal.SIGINT, service_shutdown)
    main()  # pylint: disable=no-value-for-parameter
