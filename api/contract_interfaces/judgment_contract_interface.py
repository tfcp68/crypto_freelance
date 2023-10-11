from .contract_interface_base import *

import typing
import datetime
from web3.exceptions import ContractLogicError


class JudgmentContractInterface(ContractInterfaceBase):

    @staticmethod
    def __get_contract():
        kwargs = to_dict(*get_judgment_contract_data())
        return W3.eth.contract(**kwargs)

    def __init__(self, address: str):
        super().__init__(address)
        self.__contract = self.__get_contract()(address)

    @property
    def address(self) -> str:
        return self.__contract.address

    def get_execution_contract_address(self, sender: str) -> str:
        func = self.__contract.functions.getExecutionContractAddress()
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

    def get_customer_arguments(self, sender: str) -> typing.List[Argument]:
        func = self.__contract.functions.getCustomerArguments()
        raw_data = func.call({
            "from": sender,
        })
        arguments = [Argument.from_tuple(arg) for arg in raw_data]
        return arguments

    def get_executor_arguments(self, sender: str) -> typing.List[Argument]:
        func = self.__contract.functions.getExecutorArguments()
        raw_data = func.call({
            "from": sender,
        })
        arguments = [Argument.from_tuple(arg) for arg in raw_data]
        return arguments

    def get_judgment_time_end(self, sender: str) -> datetime.datetime:
        func = self.__contract.functions.getJudgmentTimeEnd()
        time_left = func.call({
            "from": sender,
        })
        return datetime.datetime.fromtimestamp(time_left)

    def get_num_votes(self, sender: str) -> int:
        func = self.__contract.functions.getNumVotes()
        num_votes = func.call({
            "from": sender,
        })
        return num_votes

    def get_votes(self, sender: str) -> typing.Union[typing.List[JudgeVote], None]:
        func = self.__contract.functions.getVotes()
        try:
            raw_data = func.call({
                "from": sender,
            })
        except ValueError as E:
            return None
        except ContractLogicError as E:
            return None
        votes = [JudgeVote.from_tuple(data) for data in raw_data]
        return votes

    def is_closed(self, sender: str) -> bool:
        func = self.__contract.functions.isClosed()
        closed = func.call({
            "from": sender,
        })
        return closed

    def add_argument_tx(self, argument: Argument, sender: str) -> typing.Dict:
        func = self.__contract.functions.addArgument(*argument.to_raw_tuple()[:-1])
        tx = build_tx(func, sender)
        return tx

    def vote_tx(self, judge_vote: JudgeVote, sender: str):
        func = self.__contract.functions.vote(*judge_vote.to_raw_tuple())
        tx = build_tx(func, sender)
        return tx

    def check_can_sender_vote(self, sender: str) -> bool:
        func = self.__contract.functions.checkCanSenderVote(sender)
        try:
            func.call({
                "from": sender,
            })
        except ValueError as E:
            return False
        except ContractLogicError as E:
            return False
        return True

    def close(self) -> bool:
        # returns status of function:
        # True if success, False if reverted
        func = self.__contract.functions.close()
        try:
            # tx_hash = func.transact({
            #     "from": COMPANY_ACCOUNT_ADDRESS,
            # })
            tx = build_tx(func, COMPANY_ACCOUNT_ADDRESS)
            sign_tx_by_company(tx)
        except ValueError as E:
            return False
        except ContractLogicError as E:
            return False
        # W3.eth.wait_for_transaction_receipt(tx_hash)
        return True

    def get_data_view(self, sender: str) -> typing.Dict:
        data = {
            "customer_arguments": self.get_customer_arguments(sender),
            "executor_arguments": self.get_executor_arguments(sender),
            "judgment_time_end": self.get_judgment_time_end(sender),
            "num_votes": self.get_num_votes(sender),
            "votes": self.get_votes(sender),
            "closed": self.is_closed(sender),
        }
        return data
