from .contract_interface_base import *
from decimal import Decimal


class ERC20ContractInterface(ContractInterfaceBase):
    @staticmethod
    def __get_contract():
        kwargs = to_dict(*get_erc20_contract_data())
        return W3.eth.contract(**kwargs)

    def __init__(self, address: str):
        super().__init__(address)
        self.__contract = self.__get_contract()(address)

    @property
    def address(self):
        return self.__contract.address

    def balance_of(self, user: str, sender: str) -> int:
        func = self.__contract.functions.balanceOf(user)
        balance = func.call({
            "from": sender,
        })
        return balance

    def transfer_tx(self, to: str, amount: int, sender: str) -> typing.Dict:
        func = self.__contract.functions.transfer(to, amount)
        tx = build_tx(func, sender)
        return tx

    def approve_tx(self, spender: str, amount: int, sender: str) -> typing.Dict:
        func = self.__contract.functions.approve(spender, amount)
        tx = build_tx(func, sender)
        return tx

    def name(self, sender: str = COMPANY_ACCOUNT_ADDRESS) -> str:
        func = self.__contract.functions.name()
        name = func.call({
            "from": sender,
        })
        return name

    def symbol(self, sender: str = COMPANY_ACCOUNT_ADDRESS) -> str:
        func = self.__contract.functions.symbol()
        symbol = func.call({
            "from": sender,
        })
        return symbol

    def decimals(self, sender: str = COMPANY_ACCOUNT_ADDRESS) -> int:
        func = self.__contract.functions.decimals()
        decimals = func.call({
            "from": sender,
        })
        return decimals

    def to_minimal_units(self, value: Decimal) -> int:
        return int(value * 10 ** self.decimals())

    def to_decimal(self, value_in_minimal_units: int) -> Decimal:
        return Decimal(value_in_minimal_units) / 10 ** self.decimals()
