import requests

from raiden_api.model.responses import AddressResponse


class Api:
    def __init__(self, port: int, timeout: int = 60):
        self.port = port
        self.timeout = timeout

    def address(self) -> AddressResponse:
        url = f'http://localhost:{self.port}/api/1/address'
        response = requests.get(
            url,
            headers={'Content-Type': 'application/json', },
            timeout=self.timeout
        )
        return AddressResponse.from_dict(response.json())
