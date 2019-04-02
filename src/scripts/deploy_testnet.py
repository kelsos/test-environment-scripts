#!/usr/bin/env python
import json

import click
from eth_account import Account
from raiden_contracts.constants import CONTRACT_TOKEN_NETWORK_REGISTRY
from raiden_contracts.contract_manager import contract_version_string
from raiden_contracts.deploy.__main__ import (
    ContractDeployer,
    deploy_raiden_contracts,
    deploy_token_contract,
    register_token_network,
)
from web3 import HTTPProvider, Web3
from web3.middleware import geth_poa_middleware

TOKEN_DECIMALS = 18
TOKEN_SUPPLY = 10_000_000

GAS_LIMIT = 6_000_000
GAS_PRICE = 10

UNLIMITED = 115792089237316195423570985008687907853269984665640564039457584007913129639935


@click.command()
@click.option("--keystore-file", required=True, type=click.Path(exists=True, dir_okay=False))
@click.password_option("--password", envvar="ACCOUNT_PASSWORD", confirmation_prompt=False)
@click.option("--rpc-url", default="http://localhost:8545")
@click.option("--development", is_flag=True)
def main(keystore_file: str, password: str, rpc_url: str, development: bool):
    web3 = Web3(HTTPProvider(rpc_url, request_kwargs={'timeout': 60}))
    web3.middleware_stack.inject(geth_poa_middleware, layer=0)

    contract_version = '0.4.0'
    channel_participant_deposit_limit = None
    token_network_deposit_limit = None
    max_num_of_networks = None

    if development:
        contract_version = None
        channel_participant_deposit_limit = UNLIMITED
        token_network_deposit_limit = UNLIMITED
        max_num_of_networks = 500

    with open(keystore_file, 'r') as keystore:
        encrypted_key = keystore.read()
        private_key = web3.eth.account.decrypt(encrypted_key, password)
        account = Account.privateKeyToAccount(private_key)

    if private_key is None:
        print('No private key found')
        exit(1)
    owner = account.address

    if web3.eth.getBalance(owner) == 0:
        print('Account with insuficient funds.')
        exit(1)

    deployer = ContractDeployer(
        web3=web3,
        private_key=private_key,
        gas_limit=GAS_LIMIT,
        gas_price=GAS_PRICE,
        wait=10,
        contracts_version=contract_version,
    )

    print('Deploying raiden contracts')
    deployed_contract_info = deploy_raiden_contracts(
        deployer=deployer, max_num_of_token_networks=max_num_of_networks
    )
    deployed_contracts = {
        contract_name: info['address']
        for contract_name, info in deployed_contract_info['contracts'].items()
    }

    print('Deploying test token contract')
    tokens = TOKEN_SUPPLY * (10 ** TOKEN_DECIMALS)
    deployed_token = deploy_token_contract(deployer, tokens, TOKEN_DECIMALS, 'TestToken', 'TTT')

    abi = deployer.contract_manager.get_contract_abi(CONTRACT_TOKEN_NETWORK_REGISTRY)

    token_address = deployed_token['CustomToken']

    expected_version = contract_version_string(deployer.contract_version_string())

    print('Registering test token contract')
    register_token_network(
        web3=web3,
        caller=deployer.owner,
        token_registry_abi=abi,
        token_registry_address=deployed_contracts[CONTRACT_TOKEN_NETWORK_REGISTRY],
        token_address=token_address,
        token_registry_version=expected_version,
        channel_participant_deposit_limit=channel_participant_deposit_limit,
        token_network_deposit_limit=token_network_deposit_limit,
        contracts_version=deployer.contract_version_string(),
    )

    print(f'Token Deployed at: {token_address}')
    print(json.dumps(deployed_contracts, indent=4))
    print('done')


if __name__ == '__main__':
    main()
