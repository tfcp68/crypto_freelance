from .tx_storage_interface import *

from redis import Redis


class RedisTxStorage(TxStorageInterface):
    def __init__(self, *redis_args, **redis_kwargs):
        self.__redis = Redis(*redis_args, **redis_kwargs)

    def save_tx(self, tx: typing.Dict) -> str:
        tx_hash = self._hash_tx(tx)
        strigified_tx = self._pickle_tx(tx)
        self.__redis.append(tx_hash, strigified_tx)
        return tx_hash

    def get_tx(self, tx_hash: str) -> typing.Union[typing.Dict, None]:
        strigified_tx = self.__redis.get(tx_hash)
        if strigified_tx is None:
            return None
        return self._unpickle_tx(strigified_tx)

    def delete_tx(self, tx_hash: str):
        self.__redis.delete(tx_hash)
