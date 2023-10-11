import os

from api.contract_interfaces.init_web3 import W3
from .constants import *
from decimal import Decimal, getcontext
from utils_eth.tx_storages import RedisTxStorage

import typing

FAKE_ADDRESS = "0xFc36eDcE8fA8b96F743A58B776aB851E3524f55D"


def str_to_decimal_token_value(string: str) -> Decimal:
    return Decimal(string)


def eval_percent(value: int, p: int) -> int:
    return value // 100 * p


def eval_marketplace_fee(value: int) -> int:
    return value // (100 - MARKETPLACE_FEE_PERCENT) * 100 - value


def get_gas_price() -> int:
    return W3.eth.gas_price


def to_eth(wei: int) -> Decimal:
    return Decimal(wei) / W3.to_wei(1, "ether")
    # return Decimal(wei) / W3.toWei(1, "ether")


def hexify_tx(tx: typing.Dict) -> typing.Dict:
    return {
        "nonce": hex(tx["nonce"]),
        "gasPrice": hex(tx["gasPrice"]),
        "gas": hex(tx["gas"]),
        "to": tx["to"],
        "from": tx["from"],
        "value": hex(tx["value"]),
        "data": tx["data"],
        "chainId": hex(tx["chainId"]),
    }


def get_tx_receipt(tx_hash):
    tx_receipt = W3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt


def merge_dicts(base, update=None, exclude_keys: typing.Iterable = None, **kwargs):
    if update is not None:
        kwargs.update(update)
    if exclude_keys is None:
        base.update(kwargs)
        return
    for key, value in kwargs.items():
        if key not in exclude_keys:
            base[key] = value


def to_seconds(timedelta):
    if timedelta is None:
        return None
    return int(timedelta.total_seconds())


def get_tx_storage():
    host = os.environ.get("REDIS_HOST", None)
    port = os.environ.get("REDIS_PORT", None)
    assert host is not None and port is not None, "Redis tx storage configuration error"
    return RedisTxStorage(host=host, port=port)
