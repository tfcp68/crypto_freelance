from abc import ABC, abstractmethod

from api.objects import ConstTextData


class ConstTextDataDBDriverInterface(ABC):
    @abstractmethod
    def get_data(self, id: int) -> ConstTextData:
        ...

    @abstractmethod
    def put_data(self, text: str) -> ConstTextData:
        ...
