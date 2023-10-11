import os

os.environ.setdefault("WEB3_ENDPOINT", "https://rpc.sepolia.org/")

from api.contract_interfaces.init_web3 import W3

from api.contract_interfaces.utils import COMPANY_ACCOUNT_ADDRESS

print(W3.eth.get_balance(W3.eth.default_account))
# print(W3.eth.accounts)
# print(W3.eth.default_account)
