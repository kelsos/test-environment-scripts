#!/usr/bin/env bash

SCRIPT_PATH=`realpath $0`
SCRIPT_NAME=`basename $0`

SCRIPT_PATH=${SCRIPT_PATH%"/$SCRIPT_NAME"}

while getopts n:e:a:l:b:p: option
do
case "${option}"
in
n) NETWORK="${OPTARG}";;
e) ENVIROMENT="${OPTARG}";;
a) ACCOUNT="${OPTARG}";;
l) LOCAL_TRANSPORT="${OPTARG}";;
b) BINARY="${OPTARG}";;
p) PRIVATE="${OPTARG}";;
esac
done

if [[ ! "$RT_ENV__TESTING_ACCOUNTS" ]]
then
    echo "Expected accounts in environment variable TESTING_ACCOUNTS separated by colon e.g. account1:account2"
    exit 1
fi

if [[ ! "$RT_ENV__TESTING_KEYS_DIR" ]]
then
    echo 'Missing testing keys directory'
    exit 1
fi

IFS=': ' read -r -a ACCOUNTS <<< "$RT_ENV__TESTING_ACCOUNTS"

if [[ ! "$NETWORK" ]]
then
    echo 'Please specify a network'
    exit 1
fi

if [[ ! "$ACCOUNT" ]]
then
    echo 'Please specify an account'
    exit 1
fi

if [[ ! "$ENVIROMENT" ]]
then
    ENVIROMENT = 'development'
fi

NO_SYNC=''

if [[ "$NETWORK" = 'ropsten' ]]
then
    NETWORK_PORT=0
    RPC_ENDPOINT="$RT_ENV__ROPSTEN_RPC_URL"
    NETWORK_ID=3
elif [[ "$NETWORK" = 'rinkeby' ]]
then
    NETWORK_PORT=1
    RPC_ENDPOINT="$RT_ENV__RINKEBY_RPC_URL"
    NETWORK_ID=4
elif [[ "$NETWORK" = 'kovan' ]]
then
    NETWORK_PORT=2
    RPC_ENDPOINT="$RT_ENV__KOVAN_RPC_URL"
    NETWORK_ID=42
elif [[ "$NETWORK" ]]
then
    NETWORK_PORT=5
    RPC_ENDPOINT='http://localhost:8545'
    NETWORK_ID=17
    NO_SYNC="--no-sync-check"
else
    echo '-n should be "ropsten", "rinkeby" or "kovan"'
    exit 1
fi

echo "Using RPC endpoint $RPC_ENDPOINT"

if [[ "$LOCAL_TRANSPORT" = 'y' ]]
then
    echo 'using local transport'
    LOCAL_TRANSPORT="--matrix-server=http://matrix.local.raiden:8008"
else
    LOCAL_TRANSPORT=""
fi

ADDRESS="${ACCOUNTS[$ACCOUNT]}"
PORT=5"$NETWORK_PORT"0"$ACCOUNT"

WORK_DIR="$SCRIPT_PATH/logs/$NETWORK_ID/$ENVIROMENT/$ADDRESS"

echo "logs will be stored at $WORK_DIR"

if [[ ! -d "$WORK_DIR" ]]
    then
    mkdir -p "$WORK_DIR"
fi

cd "$WORK_DIR"

echo "Starting network $NETWORK on configuration $ENVIROMENT with account $ADDRESS"

if [[ ! "$BINARY" ]]
then
    echo 'Activating virtual enviroment'
    export WORKON_HOME="$HOME/.virtualenvs"
    source /usr/bin/virtualenvwrapper.sh
    workon raiden
    BINARY=raiden
else
    if [[ ! -f "$BINARY" ]]
    then
        echo "$BINARY is not a file"
        exit 1
    fi
fi

if [[ "${PRIVATE}" ]]
then
    echo "using private network configuration"
    PRIVATE_NETWORK="--tokennetwork-registry-contract-address=0xA4e13D328308194c0AB4E10bB1f2B2e8d624d240 --secret-registry-contract-address=0x1450306327242B8db9B9179906C24e5c35D4053b --endpoint-registry-contract-address=0xa427f6e3686A0BE8dE550cC5450B7FaD1B770956"
fi

echo "webui should be available shortly at http://localhost:$PORT"

${BINARY} --keystore-path  ~/.ethereum/testnet/keystore --log-config "raiden:DEBUG" --api-address localhost:"$PORT" --eth-rpc-endpoint "$RPC_ENDPOINT" --accept-disclaimer --network-id "$NETWORK_ID" --environment-type  "$ENVIROMENT" --address "$ADDRESS" --password-file "$RT_ENV__TESTING_KEYS_DIR/$ADDRESS" ${LOCAL_TRANSPORT} ${NO_SYNC} ${PRIVATE_NETWORK}

