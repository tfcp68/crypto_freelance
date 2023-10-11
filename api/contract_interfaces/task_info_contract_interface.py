from .contract_interface_base import *
from .erc20_contract_interface import ERC20ContractInterface

import datetime
import typing
from web3.exceptions import ContractLogicError


class TaskInfoContractInterface(ContractInterfaceBase):
    def __init__(self, address: str):
        super().__init__(address)
        kwargs = to_dict(*get_task_info_contract_data())
        self.__contract = W3.eth.contract(address=address, **kwargs)

    @property
    def address(self):
        return self.__contract.address

    def get_customer(self, sender: str) -> str:
        func = self.__contract.functions.getCustomer()
        customer = func.call({
            "from": sender,
        })
        return customer

    def get_task_data(self, sender: str) -> TaskData:
        func = self.__contract.functions.getTaskData()
        task_data_raw = func.call({
            "from": sender,
        })
        task_data = TaskData.from_tuple(task_data_raw)
        return task_data

    def get_task_execution_time(self, sender: str) -> datetime.timedelta:
        func = self.__contract.functions.getTaskExecutionTime()
        execution_time = func.call({
            "from": sender,
        })
        return datetime.timedelta(seconds=execution_time)

    def get_price(self, sender: str) -> int:
        func = self.__contract.functions.getPrice()
        price = func.call({
            "from": sender,
        })
        return price

    def get_security_deposit(self, sender: str) -> int:
        func = self.__contract.functions.getSecurityDeposit()
        security_deposit = func.call({
            "from": sender,
        })
        return security_deposit

    def get_executor(self, sender: str) -> typing.Union[str, None]:
        func = self.__contract.functions.getExecutor()
        try:
            executor = func.call({
                "from": sender,
            })
        except ValueError as E:
            executor = None
        except ContractLogicError as E:
            executor = None
        return executor

    def get_solution(self, sender: str) -> typing.Union[typing.List[SolutionData], None]:
        func = self.__contract.functions.getSolution()
        try:
            solution_raw = func.call({
                "from": sender,
            })
        except ValueError as E:
            return None
        except ContractLogicError as E:
            return None
        solution = [SolutionData.from_tuple(solution_) for solution_ in solution_raw]
        return solution

    def get_token_address(self, sender: str) -> str:
        func = self.__contract.functions.getTokenAddress()
        token_address = func.call({
            "from": sender,
        })
        return token_address

    def get_token(self, sender: str) -> ERC20ContractInterface:
        token_address = self.get_token_address(sender)
        return ERC20ContractInterface(token_address)

    def get_data_view(self, sender: str) -> typing.Dict:
        data = {
            "token_name": self.get_token(sender).name(sender),
            "address": self.address,
            "customer": self.get_customer(sender),
            "task_data": self.get_task_data(sender),
            "task_execution_time": self.get_task_execution_time(sender),
            "price": self.get_price(sender),
            "security_deposit": self.get_security_deposit(sender),
            "executor": self.get_executor(sender),
            "solution": self.get_solution(sender),
        }
        return data
