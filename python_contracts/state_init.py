from dataclasses import dataclass


@dataclass
class StateInit:
    address: str
    initial: str
    fee: int
