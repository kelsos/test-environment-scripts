#!/usr/bin/env python
import click
from eth_account import Account
from raiden_contracts.constants import CONTRACT_TOKEN_NETWORK_REGISTRY
from raiden_contracts.deploy.__main__ import ContractDeployer, deploy_raiden_contracts, deploy_token_contract, \
    register_token_network
from web3 import HTTPProvider, Web3
from web3.middleware import geth_poa_middleware

TOKEN_DECIMALS = 18
TOKEN_SUPPLY = 10_000_000

GAS_LIMIT = 6_000_000
GAS_PRICE = 10


@click.command()
@click.option("--keystore-file", required=True, type=click.Path(exists=True, dir_okay=False))
@click.password_option("--password", envvar="ACCOUNT_PASSWORD", required=True, confirmation_prompt=False)
@click.option("--rpc-url", default="http://localhost:8545")
def main(keystore_file: str, password: str, rpc_url: str):
    web3 = Web3(HTTPProvider(rpc_url, request_kwargs={'timeout': 60}))
    web3.middleware_stack.inject(geth_poa_middleware, layer=0)

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

    deployer = ContractDeployer(web3, private_key, GAS_LIMIT, GAS_PRICE)

    print('Deploying raiden contracts')
    deployed_contract_info = deploy_raiden_contracts(deployer)
    deployed_contracts = {
        contract_name: info['address']
        for contract_name, info in deployed_contract_info['contracts'].items()
    }

    print('Deploying test token contract')
    deployed_token = deploy_token_contract(deployer, TOKEN_SUPPLY, TOKEN_DECIMALS, 'TestToken', 'TTT')

    abi = deployer.contract_manager.get_contract_abi(CONTRACT_TOKEN_NETWORK_REGISTRY)

    token_address = deployed_token['CustomToken']

    print('Registering test token contract')
    register_token_network(
        web3=web3,
        private_key=private_key,
        token_registry_abi=abi,
        token_registry_address=deployed_contracts[CONTRACT_TOKEN_NETWORK_REGISTRY],
        token_address=token_address
    )

    print(f'Token Deployed at: {token_address}')
    print(deployed_contracts)
    print('done')


if __name__ == '__main__':
    main()
