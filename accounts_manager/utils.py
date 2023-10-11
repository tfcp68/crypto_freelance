from api.contract_interfaces.init_web3 import W3
from api.contract_interfaces import ERC20ContractInterface
from api.contract_interfaces.utils import COMPANY_ACCOUNT_ADDRESS, COMPANY_PK, DEFAULT_GAS_AMOUNT
from eth.allowed_tokens import USDT, TON
from decimal import Decimal


def pay_test_balance(address: str):
    # __send_eth(address)
    __send_token(address, USDT)
    __send_token(address, TON)


def __send_eth(address):
    tx = {
        "from": COMPANY_ACCOUNT_ADDRESS,
        "to": address,
        "value": W3.to_wei(100, "ether"),
        "nonce": W3.eth.get_transaction_count(COMPANY_ACCOUNT_ADDRESS),
        "gas": DEFAULT_GAS_AMOUNT,
        "gasPrice": W3.eth.gas_price,
    }
    __sign_tx(tx)


def __send_token(to, token):
    amount = token.to_minimal_units(Decimal(1000000))
    tx = token.transfer_tx(to, amount, COMPANY_ACCOUNT_ADDRESS)
    __sign_tx(tx)


def __sign_tx(tx):
    estimated_gas_amount = W3.eth.estimate_gas(tx, "latest")
    tx["gas"] = estimated_gas_amount
    signed_tx = W3.eth.account.sign_transaction(tx, COMPANY_PK)
    tx_hash = W3.eth.send_raw_transaction(signed_tx.rawTransaction)
    W3.eth.wait_for_transaction_receipt(tx_hash)
