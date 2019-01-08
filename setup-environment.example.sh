#!/usr/bin/env bash

RT_ENV__SCRIPT_PATH=`realpath $0`
RT_ENV__SCRIPT_NAME=`basename $0`

RT_ENV__SCRIPT_PATH=${RT_ENV__SCRIPT_PATH%"$RT_ENV__SCRIPT_NAME"}

export RT_ENV__TESTING_ACCOUNTS=''
export RT_ENV__TESTING_KEYS_DIR=${RT_ENV__SCRIPT_PATH}/credentials

export RT_ENV__ROPSTEN_RPC_URL=''
export RT_ENV__KOVAN_RPC_URL=''
export RT_ENV__RINKEBY_RPC_URL=''

alias raiden-up="$RT_ENV__SCRIPT_PATH/raiden-up.sh"
alias dev-chain-reset='parity --chain dev db kill'
alias raiden-test="cd $RT_ENV__SCRIPT_PATH"