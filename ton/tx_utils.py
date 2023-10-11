from decimal import Decimal
import typing
from .money_utils import to_nano


def make_tx(to: str, value: typing.Union[Decimal, str], state_init: str, data: str = None) -> typing.Dict:
    tx = {
        "to": to,
        "value": str(to_nano(value)),
        "stateInit": state_init
    }
    if data is not None:
        tx["data"] = data
        tx["dataType"] = "boc"
    return tx
