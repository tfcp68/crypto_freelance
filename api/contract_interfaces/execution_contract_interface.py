import datetime

from .contract_interface_base import *
from web3.exceptions import ContractLogicError


class ExecutionContractInterface(ContractInterfaceBase):

    @staticmethod
    def __get_contract():
        kwargs = to_dict(*get_executing_contract_data())
        return W3.eth.contract(**kwargs)

    def __init__(self, address: str):
        super().__init__(address)
        self.__contract = self.__get_contract()(address)

    @property
    def address(self) -> str:
        return self.__contract.address

    @classmethod
    def get_judgment_contract_address(cls, tx_receipt) -> str:
        event = cls.__get_contract().events.Closed().process_receipt(tx_receipt)[0]
        return event["args"]["judgmentContractAddress"]

    def get_execution_time_end(self, sender: str) -> typing.Union[datetime.datetime, None]:
        func = self.__contract.functions.getExecutionTimeEnd()
        try:
            execution_time_end = func.call({
                "from": sender,
            })
        except ValueError as E:
            return None
        except ContractLogicError as E:
            return None
        return datetime.datetime.fromtimestamp(execution_time_end)

    def get_make_deal_contract_address(self, sender: str) -> str:
        func = self.__contract.functions.getMakeDealContractAddress()
        address = func.call({
            "from": sender,
        })
        return address

    def get_task_info_contract_address(self, sender: str) -> str:
        func = self.__contract.functions.getTaskInfoContractAddress()
        address = func.call({
            "from": sender,
        })
        return address

    # def start_execution_tx(self, sender: str) -> typing.Dict:
    #     func = self.__contract.functions.startExecution()
    #     tx = build_tx(func, sender)
    #     return tx

    def finish_execution_tx(self, sender: str) -> typing.Dict:
        func = self.__contract.functions.finishExecution()
        tx = build_tx(func, sender)
        return tx

    def add_solution_tx(self, solution_data: SolutionData, sender: str) -> typing.Dict:
        func = self.__contract.functions.addSolution(*solution_data.to_raw_tuple()[:-1])
        tx = build_tx(func, sender)
        return tx

    def add_execution_time_tx(self, additional_time: datetime.timedelta, sender: str) -> typing.Dict:
        func = self.__contract.functions.addExecutionTime(int(additional_time.total_seconds()))
        tx = build_tx(func, sender)
        return tx

    def accept_solution_tx(self, sender: str) -> typing.Dict:
        func = self.__contract.functions.acceptSolution()
        tx = build_tx(func, sender)
        return tx

    def deny_solution_tx(self, judgment_time: datetime.timedelta, sender: str) -> typing.Dict:
        func = self.__contract.functions.denySolution(int(judgment_time.total_seconds()))
        tx = build_tx(func, sender)
        return tx
        # events = self.__closed_event_filter.get_new_entries()
        # event = events[-1]
        # return event.args.judgmentContractAddress

    def get_data_view(self, sender: str) -> typing.Dict:
        data = {
            "address": self.address,
            "execution_time_end": self.get_execution_time_end(sender),
        }
        return data

    def close(self) -> bool:
        # returns status of function:
        # True if success, False if reverted
        sender = COMPANY_ACCOUNT_ADDRESS
        func = self.__contract.functions.close()
        try:
            # tx_hash = func.transact({
            #     "from": sender,
            # })
            tx = build_tx(func, sender)
            sign_tx_by_company(tx)
        except ValueError as E:
            return False
        except ContractLogicError as E:
            return False
        # W3.eth.wait_for_transaction_receipt(tx_hash)
        return True
