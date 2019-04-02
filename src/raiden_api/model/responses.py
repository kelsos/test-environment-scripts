import typing


class AddressResponse:
    def __init__(self, our_address: str):
        self.our_address = our_address

    @classmethod
    def from_dict(cls, data: typing.Dict[str, typing.Any]) -> 'AddressResponse':
        return cls(our_address=str(data['our_address']))


class PaymentResponse:
    def __init__(
        self,
        initiator_address: str,
        target_address: str,
        token_address: str,
        amount: int,
        identifier: int,
    ):
        self.initiator_address = initiator_address
        self.target_address = target_address
        self.token_address = token_address
        self.amount = amount
        self.identifier = identifier

    @classmethod
    def from_dict(cls, data: typing.Dict[str, typing.Any]) -> 'PaymentResponse':
        response = cls(
            initiator_address=str(data['initiator_address']),
            target_address=str(data['target_address']),
            token_address=str(data['token_address']),
            amount=int(data['amount']),
            identifier=int(data['identifier']),
        )

        return response
