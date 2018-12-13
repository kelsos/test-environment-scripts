import typing


class AddressResponse:

    def __init__(self, our_address: str):
        self.our_address = our_address

    @classmethod
    def from_dict(cls, data: typing.Dict[str, typing.Any]) -> 'AddressResponse':
        return cls(our_address=str(data['our_address']))
