import typing
from .constants import FEE_PERCENT


def to_nano(value: float) -> int:
    return int(float(value) * int(1e9))


def from_nano(value: int) -> float:
    return value / int(1e9)


def eval_fee(price_nano):
    return price_nano // (100 - FEE_PERCENT)
