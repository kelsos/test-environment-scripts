#!/usr/bin/env bash

url_decode(){
  echo -e "$(sed 's/+/ /g;s/%\(..\)/\\x\1/g;')"
}

URL=$1

if [[ ! -d "./tmp" ]]
then
    mkdir -p "./tmp"
fi

wget -P ./tmp ${URL}

DECODED_URL=`echo ${URL} | url_decode`
FILENAME=${DECODED_URL##*/}

TEMP_LOCATION="./tmp/${FILENAME}"

tar -zxvf ${TEMP_LOCATION} -C ./bin/

rm -f "${TEMP_LOCATION}"

rmdir "./tmp"

echo 'Done'