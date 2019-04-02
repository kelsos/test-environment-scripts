#!/usr/bin/env python
import json
import sys

import click
from eth_account.account import Account
from eth_utils import to_checksum_address
from web3 import Web3
from web3.providers import HTTPProvider

WEI_TO_ETH = 10 ** 18
ERC20_ABI = json.loads(
    '[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_from","type":"address"},{"indexed":true,"name":"_to","type":"address"},{"indexed":false,"name":"_value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_owner","type":"address"},{"indexed":true,"name":"_spender","type":"address"},{"indexed":false,"name":"_value","type":"uint256"}],"name":"Approval","type":"event"}]'
)  # noqa: 501


@click.command()
@click.option("--keystore-file", required=True, type=click.Path(exists=True, dir_okay=False))
@click.password_option("--password", envvar="ACCOUNT_PASSWORD", required=True)
@click.option("--rpc-url", default="http://localhost:8545")
@click.option('--accounts', envvar="RT_ENV__TESTING_ACCOUNTS", required=True)
@click.option('--token', required=True)
@click.option('--amount', default=1, type=float)
def main(
    keystore_file: str, password: str, rpc_url: str, accounts: str, token: str, amount: float
):
    testing_accounts = accounts.split(':')

    web3 = Web3(HTTPProvider(rpc_url))

    with open(keystore_file, 'r') as keystore:
        encrypted_key = keystore.read()
        private_key = web3.eth.account.decrypt(encrypted_key, password)
        account = Account.privateKeyToAccount(private_key)

    checksum_address = to_checksum_address(account.address)
    print(f'Using account {checksum_address} to fund {len(testing_accounts)} accounts')

    sender = checksum_address
    erc20 = web3.eth.contract(address=token, abi=ERC20_ABI)

    wei_amount = int(amount * WEI_TO_ETH)

    send_tokens(web3, sender, wei_amount, testing_accounts, erc20, private_key)


def send_tokens(web3, sender, amount, testing_accounts, contract, private_key):
    balance = contract.functions.balanceOf(sender).call()

    print(f'Sender ({sender}) has {balance} tokens')

    for receiver in testing_accounts:
        balance = contract.functions.balanceOf(receiver).call()

        if balance > 0:
            print(f'skipping {receiver} due to non-zero balance')
            continue

        transfer(web3, receiver, sender, amount, contract, private_key)


def transfer(web3: Web3, receiver: str, sender: str, wei_value: int, contract, private_key):
    nonce = web3.eth.getTransactionCount(sender)

    print(f'preparing to transfer {wei_value} to {receiver} [{nonce}]')

    transfer_tx = contract.functions.transfer(receiver, wei_value).buildTransaction(
        {
            'chainId': web3.net.chainId,
            'gas': 70000,
            'gasPrice': web3.toWei('1', 'gwei'),
            'nonce': nonce,
        }
    )

    signed_txn = web3.eth.account.signTransaction(transfer_tx, private_key=private_key)
    tx_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    transaction_receipt = web3.eth.waitForTransactionReceipt(tx_hash)

    if transaction_receipt['status'] == 1:
        balance = contract.functions.balanceOf(receiver).call()
        print(f'{receiver} has a balance of {balance}')
    else:
        print(print(f'transaction to {receiver} failed'))


def unlock_account(web3: Web3, address: str, passphrase: str):
    if not web3.personal.unlockAccount(address, passphrase):
        print('Failed to unlock prefunded')
        sys.exit(1)


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
