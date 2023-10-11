from abc import ABC, abstractmethod

import typing
from hashlib import sha256
import pickle


class TxStorageInterface(ABC):
    @abstractmethod
    def save_tx(self, tx: typing.Dict) -> str:
        # returns sha256 hash of tx, which could be used to getting tx
        ...

    @abstractmethod
    def get_tx(self, tx_hash: str) -> typing.Union[typing.Dict, None]:
        # returns None if not tx with tx_hash in storage
        # else returns tx by tx_hash
        ...

    @abstractmethod
    def delete_tx(self, tx_hash: str):
        # removes tx from storage by tx_hash
        ...

    @staticmethod
    def _pickle_tx(tx: typing.Dict) -> bytes:
        return pickle.dumps(tx)

    @staticmethod
    def _unpickle_tx(jsonified_tx: bytes) -> typing.Dict:
        return pickle.loads(jsonified_tx)

    @staticmethod
    def _hash_tx(tx: typing.Dict) -> str:
        strigified = TxStorageInterface._pickle_tx(tx)
        return str(sha256(strigified).hexdigest())
