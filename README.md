Collection of utilities to bootstrap a small raiden network.
-------

# About the environment

The environment uses [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) to manage the python
virtual environments and most of the scripts and utilities are configured around that fact.


# Setting up the environment

For the private chain setup to work you need to have parity installed since the setup uses a [Parity Dev Chain](https://wiki.parity.io/Private-development-chain)

You can start by copying the example setup and getting your setup ready.

```bash
cp setup-environment.example.sh setup-environment.sh
```

Then source the `setup-environment.sh` to load the environment.

```bash
source setup-environment.sh
```

This provides an alias `raiden-up` that can be used to easily start raiden nodes.
This also provides the `dev-chain-reset` alias that is used to reset the development chain.

In the `setup-environment.sh` script the accounts should be `:` separated

```bash
export TESTING_ACCOUNTS='account1:account2:account3'
```

The passphrases should be stored in individual text files with filenames 'account1', 'account2' etc with the passphrase inside.
The account name should be prefixed with `0x` and the account should be in checksum format.


# Using the script

Then you can call the script 
```bash
➜ raiden-up -n rinkeby -a 0 -e production -l y
```

# Available flags

The following flags are available for the script.

* -n: network (can be 'rinkeby', 'ropsten' or 'kovan')
* -a: account (the index of the account in `TESTING_ACCOUNTS` 0 is the first account)
* -e: environment (production/development)
* -l: local transport **y** (if the option is specified the *transport01.raiden.network* is used instead)
* -b: path to the binary. (If not specified it will used raiden from the virtual enviroment else it will use the specified binary)
* -p: private chain setup. (This will pass information to raiden to work with the private chain) *You might need to change the addresses dependending on the deployment on the parity dev chain)


# Starting a the private chain

This is a small utility that starts a parity dev chain with RPC enabled.
It also funds the accounts that are in the `TESTING_ACCOUNTS` environment variable and then
sends a single transfer from the default account to the first account every `--block-time` seconds
to simulate a stable block time.


```bash
./start_private_chain.py --block-time=1   
```

# Deploying the raiden smart contracts

## Before installing

You can run the `solidity.sh` script to install the proper version of `solc` in your virtual environment to be able to 
compile the `raiden-contracts`. Currently the compilation process fails with solidity `0.5.0`.

# Installation
 
In order for the private raiden network to work you need to deploy the smart contracts on your private chain.

```bash
python -m raiden_contracts.deploy raiden --rpc-provider http://127.0.0.1:8545 --private-key /home/kelsos/.ethereum/testnet/keystore/0x82641569b2062B545431cF6D7F0A418582865ba7 --gas-price 10 --gas-limit 6000000   
```

## Deploying the test contract

```bash
python -m raiden_contracts.deploy token --rpc-provider http://127.0.0.1:8545 --private-key /home/kelsos/.ethereum/testnet/keystore/0x82641569b2062B545431cF6D7F0A418582865ba7 --gas-price 10 --token-supply 10000000 --token-name TestToken --token-decimals 18 --token-symbol TTT
```

## Registering the test token

```bash 
python -m raiden_contracts.deploy register --rpc-provider http://127.0.0.1:8545 --private-key /home/kelsos/.ethereum/testnet/keystore/0x82641569b2062B545431cF6D7F0A418582865ba7 --gas-price 10 --token-address 0x28104EE15e1c70c421150865C3fb731c426929E6 --registry-address 0xA4e13D328308194c0AB4E10bB1f2B2e8d624d240

```

Currently `raiden-contracts` doesn't support a single command deployment of all the contracts (raiden, token) along 
with the registration. For this reason `scripts/deploy_testnet.py` is a script that is patched together from the 
[deploy script](https://github.com/raiden-network/raiden-contracts/blob/master/raiden_contracts/deploy/__main__.py)
that helps you deploy everything in a single command.

# Funding the accounts

```bash
./send_tokens.py --keystore-file ~/.ethereum/testnet/keystore/0x82641569b2062B545431cF6D7F0A418582865ba7 --password 123 --token 0x28104EE15e1c70c421150865C3fb731c426929E6

```

# Running the transfers

```bash
./run_transfers.py --token 0x28104EE15e1c70c421150865C3fb731c426929E6 --config nodes.yml
```

# Using raiden-up for a local node

```bash
raiden-up -n local -a 3 -e production -p true -l y
```

# Running a local synapse (matrix server) 

> Currently using a local synapse version is not working due to a crash on raiden client.

Run `tools\install_synapse.sh` from the [raiden repo](https://github.com/raiden-network/raiden/blob/master/tools/install_synapse.sh)

After synapse is installed then you can go to run synapse by executing `run_synapse.sh` from the directory where synapse was installed in the previous script.

Add the url of the local matrix server to your hosts file:
```bash
# Static table lookup for hostnames.
# See hosts(5) for details.
127.0.0.1 matrix.local.raiden

```