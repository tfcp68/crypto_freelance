from abc import ABC, abstractmethod

from .init_web3 import W3
from .objects import *
from .utils import *


class ContractInterfaceBase(ABC):
    def __init__(self, address: str):
        ...

    @abstractmethod
    def address(self) -> str:
        ...

    def get_data_view(self, sender: str) -> typing.Dict:
        ...
