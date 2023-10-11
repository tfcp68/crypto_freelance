from api.contract_interfaces.init_web3 import W3
from api.contract_interfaces.utils import to_dict, __get_contract_data, COMPANY_ACCOUNT_ADDRESS, sign_tx_by_company, \
    build_tx

import typing


def get_usdt_contract_data() -> typing.Dict:
    contract_file_name = "USDT.sol"
    return to_dict(*__get_contract_data(contract_file_name))


def get_ton_contract_data() -> typing.Dict:
    contract_file_name = "TonCoin.sol"
    return to_dict(*__get_contract_data(contract_file_name))


def get_contract(kwargs):
    return W3.eth.contract(**kwargs)


def place_contract(contract) -> str:
    tx = build_tx(contract.constructor(), COMPANY_ACCOUNT_ADDRESS)
    tx_receipt = sign_tx_by_company(tx)
    # tx_hash = contract.constructor().transact({
    #     "from": COMPANY_ACCOUNT_ADDRESS,
    # })
    # tx_receipt = W3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt.contractAddress


if __name__ == "__main__":
    usdt_address = place_contract(get_contract(get_usdt_contract_data()))
    print("USDT:", usdt_address)
    ton_address = place_contract(get_contract(get_ton_contract_data()))
    print("TON:", ton_address)
