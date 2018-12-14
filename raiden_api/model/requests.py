import time
import typing


class PaymentRequest:
    def __init__(self, amount: int, identifier: int = None):
        self.amount = amount
        self.identifier = identifier

        if identifier is None:
            self.identifier = time.time()

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        result = {
            'amount': self.amount,
            'identifier': self.identifier,
        }

        return result
