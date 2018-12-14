#!/usr/bin/env bash
set -ex

SOLC_URL="https://github.com/ethereum/solidity/releases/download/v0.4.25/solc-static-linux"
SOLC_BIN="${VIRTUAL_ENV}/bin/solc"

( [[ -x ${SOLC_BIN} ]] || ( wget ${SOLC_URL} -O ${SOLC_BIN} && chmod +x ${SOLC_BIN} ) )