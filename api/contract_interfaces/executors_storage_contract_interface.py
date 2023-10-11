from .contract_interface_base import *


class ExecutorsStorageContractInterface(ContractInterfaceBase):
    @staticmethod
    def __get_contract():
        kwargs = to_dict(*get_executors_storage_contract_data())
        return W3.eth.contract(**kwargs)

    def __init__(self, address: str):
        super().__init__(address)
        self.__contract = self.__get_contract()(address)

    @property
    def address(self) -> str:
        return self.__contract.address

    def get_executors(self, sender: str, filter_by: bool = None) -> typing.List[ExecutorData]:
        """
        If filter_by is True then will be returned only chosen executors.
        If filter_by is False then will be returned only not chosen executors.
        If filter_by is None then will be returned all executors.
        """
        func = self.__contract.functions.getExecutors()
        executors_raw = func.call({
            "from": sender,
        })
        executors = [ExecutorData.from_tuple(executor_) for executor_ in executors_raw \
                     if filter_by is None or executor_[1] is filter_by]
        return executors
