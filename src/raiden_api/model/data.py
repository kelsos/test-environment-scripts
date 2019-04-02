import typing


class Channel:
    def __init__(
        self,
        token_network_identifier: str,
        channel_identifier: int,
        partner_address: str,
        token_address: str,
        balance: int,
        total_deposit: int,
        state: str,
        settle_timeout: int,
        reveal_timeout: int,
    ):
        self.token_network_identifier = token_network_identifier
        self.channel_identifier = channel_identifier
        self.partner_address = partner_address
        self.token_address = token_address
        self.balance = balance
        self.total_deposit = total_deposit
        self.state = state
        self.settle_timeout = settle_timeout
        self.reveal_timeout = reveal_timeout

    @classmethod
    def from_dict(cls, data: typing.Dict[str, typing.Any]) -> 'Channel':
        response = cls(
            token_network_identifier=str(data['token_network_identifier']),
            channel_identifier=int(data['channel_identifier']),
            partner_address=str(data['partner_address']),
            token_address=str(data['token_address']),
            balance=int(data['balance']),
            total_deposit=int(data['total_deposit']),
            state=str(data['state']),
            settle_timeout=int(data['settle_timeout']),
            reveal_timeout=int(data['reveal_timeout']),
        )

        return response
