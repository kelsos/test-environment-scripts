import requests

from raiden_api.model.exceptions import HttpErrorException
from raiden_api.model.requests import PaymentRequest
from raiden_api.model.responses import AddressResponse, PaymentResponse


class Api:
    __headers = {'Content-Type': 'application/json'}

    def __init__(self, port: int, timeout: int = 60):
        self.port = port
        self.timeout = timeout
        self.__api_base = f'http://localhost:{self.port}/api/v1'

    def address(self) -> AddressResponse:
        url = f'{self.__api_base}/address'

        response = requests.get(
            url,
            headers=self.__headers,
            timeout=self.timeout
        )

        json = response.json()

        if response.status_code != 200:
            raise HttpErrorException(response.status_code, json['errors'])

        return AddressResponse.from_dict(json)

    def payment(self, receiver: str, request: PaymentRequest, token: str) -> PaymentResponse:
        url = f'{self.__api_base}/payments/{token}/{receiver}'
        response = requests.post(
            url,
            headers=self.__headers,
            json=request.to_dict(),
            timeout=self.timeout
        )

        json = response.json()

        if response.status_code != 200:
            raise HttpErrorException(response.status_code, json['errors'])

        return PaymentResponse.from_dict(json)
