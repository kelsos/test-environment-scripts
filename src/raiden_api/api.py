from typing import Any, Dict, List

import requests

from raiden_api.model.data import Channel
from raiden_api.model.exceptions import HttpErrorException
from raiden_api.model.requests import ManageChannelRequest, OpenChannelRequest, PaymentRequest
from raiden_api.model.responses import AddressResponse, PaymentResponse


def get_errors(json: Dict[str, Any]) -> str:
    result = ''
    if 'errors' in json:
        result = json['errors']

    return result


class Api:
    __headers = {'Content-Type': 'application/json'}

    def __init__(self, port: int, timeout: int = 900):
        self.port = port
        self.timeout = timeout
        self.__api_base = f'http://localhost:{self.port}/api/v1'

    def address(self) -> AddressResponse:
        url = f'{self.__api_base}/address'

        response = requests.get(url, headers=self.__headers, timeout=self.timeout)

        json = response.json()

        if response.status_code != 200:
            raise HttpErrorException(response.status_code, get_errors(json))

        return AddressResponse.from_dict(json)

    def payment(self, receiver: str, request: PaymentRequest, token: str) -> PaymentResponse:
        url = f'{self.__api_base}/payments/{token}/{receiver}'
        response = requests.post(
            url, headers=self.__headers, json=request.to_dict(), timeout=self.timeout
        )

        json = response.json()

        if response.status_code != 200:
            raise HttpErrorException(response.status_code, get_errors(json))

        return PaymentResponse.from_dict(json)

    def channels(self) -> List[Channel]:
        url = f'{self.__api_base}/channels'

        response = requests.get(url, headers=self.__headers, timeout=self.timeout)

        json = response.json()

        if response.status_code != 200:
            raise HttpErrorException(response.status_code, get_errors(json))

        channels = []

        for channel in json:
            channels.append(Channel.from_dict(channel))

        return channels

    def open_channel(self, request: OpenChannelRequest) -> Channel:
        url = f'{self.__api_base}/channels'
        response = requests.put(
            url, headers=self.__headers, json=request.to_dict(), timeout=self.timeout
        )

        json = response.json()

        if response.status_code != 201:
            raise HttpErrorException(response.status_code, get_errors(json))

        return Channel.from_dict(json)

    def manage_channel(
        self, request: ManageChannelRequest, token_address: str, partner_address: str
    ) -> Channel:
        url = f'{self.__api_base}/channels/{token_address}/{partner_address}'
        response = requests.patch(
            url, headers=self.__headers, json=request.to_dict(), timeout=self.timeout
        )

        json = response.json()
        if response.status_code != 200:
            raise HttpErrorException(response.status_code, get_errors(json))

        return Channel.from_dict(json)
