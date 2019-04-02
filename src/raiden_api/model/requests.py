import time
import typing


class PaymentRequest:
    def __init__(self, amount: int, identifier: int = None):
        self.amount = amount
        self.identifier = identifier

        if identifier is None:
            self.identifier = int(time.time())

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        result = {'amount': self.amount, 'identifier': self.identifier}

        return result


class OpenChannelRequest:
    def __init__(
        self,
        partner_address: str,
        token_address: str,
        total_deposit: int,
        settle_timeout: int = 500,
    ):
        self.partner_address = partner_address
        self.token_address = token_address
        self.total_deposit = total_deposit
        self.settle_timeout = settle_timeout

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        result = {
            'partner_address': self.partner_address,
            'token_address': self.token_address,
            'total_deposit': self.total_deposit,
            'settle_timeout': self.settle_timeout,
        }

        return result


class ManageChannelRequest:
    def __init__(self, total_deposit: int = None, state: str = None):
        assert state is None or state == 'closed'
        self.total_deposit = total_deposit
        self.state = state

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        result: typing.Dict[str, typing.Any] = {}

        if self.total_deposit:
            result['total_deposit'] = self.total_deposit

        if self.state:
            result['state'] = self.state

        return result
