#!/usr/bin/env bash

SCRIPT_PATH=`realpath $0`
SCRIPT_NAME=`basename $0`

SCRIPT_PATH=${SCRIPT_PATH%"$SCRIPT_NAME"}

export TESTING_ACCOUNTS=''
export TESTING_KEYS_DIR=${SCRIPT_PATH}/credentials

export ROPSTEN_RPC_URL=''
export KOVAN_RPC_URL=''
export RINKEBY_RPC_URL=''

alias raiden-up='"$SCRIPT_PATH"/raiden-up.sh'
alias dev-chain-reset='parity --chain dev db kill'