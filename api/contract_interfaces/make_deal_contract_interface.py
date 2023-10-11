from .contract_interface_base import *
from .executors_storage_contract_interface import ExecutorsStorageContractInterface

import datetime


class MakeDealContractInterface(ContractInterfaceBase):

    @staticmethod
    def __get_contract():
        kwargs = to_dict(*get_make_deal_contract_data())
        return W3.eth.contract(**kwargs)

    def __init__(self, address: str):
        super().__init__(address)
        self.__contract = self.__get_contract()(address)

    @classmethod
    def new_contract_tx(cls,
                        token: str,
                        task_id: int,
                        task_hashsum: str,
                        task_execution_time: datetime.timedelta,
                        price: int,
                        security_deposit_part: int,
                        sender: str
                        ):
        contract = cls.__get_contract().constructor(
            token,
            task_id,
            to_bytes(task_hashsum),
            int(task_execution_time.total_seconds()),
            int(price),
            int(security_deposit_part),
        )
        tx = build_tx(contract, sender)
        return tx

    @property
    def address(self) -> str:
        return self.__contract.address

    @classmethod
    def get_execution_contract_address(cls, tx_receipt) -> str:
        event = cls.__get_contract().events.Closed().process_receipt(tx_receipt)[0]
        return event["args"]["executionContractAddress"]

    def get_task_info_contract_address(self, sender: str) -> str:
        func = self.__contract.functions.getTaskInfoContractAddress()
        address = func.call({
            "from": sender,
        })
        return address

    def get_executors(self, sender: str, filter_by: bool = None) -> typing.List[ExecutorData]:
        """
        If filter_by is True then will be returned only chosen executors.
        If filter_by is False then will be returned only not chosen executors.
        If filter_by is None then will be returned all executors.
        """
        func = self.__contract.functions.getExecutorsStorageContractAddress()
        address = func.call({
            "from": sender,
        })
        executors_storage_contract = ExecutorsStorageContractInterface(address)
        return executors_storage_contract.get_executors(sender, filter_by)

    def is_activated(self, sender: str) -> bool:
        func = self.__contract.functions.isActivated()
        activated = func.call({
            "from": sender,
        })
        return activated

    def count_money_distribution(self, sender: str) -> MakeDealMoneyDistribution:
        func = self.__contract.functions.countMoneyDistribution()
        raw_data = func.call({
            "from": sender,
        })
        money_distribution = MakeDealMoneyDistribution.from_tuple(raw_data)
        return money_distribution

    def activate_tx(self, sender: str) -> typing.Dict:
        func = self.__contract.functions.activate()
        tx = build_tx(func, sender)
        return tx

    def respond_tx(self, sender: str) -> typing.Dict:
        func = self.__contract.functions.respond()
        tx = build_tx(func, sender)
        return tx

    def choose_executors_tx(self, chosen_executors: typing.List[str], sender: str) -> typing.Dict:
        func = self.__contract.functions.chooseExecutors(chosen_executors)
        tx = build_tx(func, sender)
        return tx

    def accept_invitation_tx(self, sender: str) -> typing.Dict:
        func = self.__contract.functions.acceptInvitation()
        tx = build_tx(func, sender)
        return tx
        # event_list = self.__deal_event_filter.get_new_entries()
        # event = event_list[-1]
        # return event.args.executingContractAddress

    def get_data_view(self, sender: str) -> typing.Dict:
        data = {
            "address": self.address,
            "executors": self.get_executors(sender),
            "activated": self.is_activated(sender),
        }
        return data
