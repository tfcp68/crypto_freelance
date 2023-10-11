from pathlib import Path
import json
import typing
from .init_web3 import W3
from .constants import *


# DEFAULT_GAS_AMOUNT = 10000000
# COMPANY_ACCOUNT_ADDRESS = "0x51Ad12B530b1F1a5E3343ae3E5105048C644f59d"
# COMPANY_PK = "e996e69077dbed1cb365cbf776a1e6cb4e814d83307e3e5d22ff6bfcd3408fe8"

# ERC20_TOKEN_CONTRACT_ADDRESS = "0x0741fB496E58A1Fbc8cb9Ef9E096393e62582613"


def to_dict(abi, bin, bin_runtime):
    return {
        "abi": abi,
        "bytecode": bin,
        "bytecode_runtime": bin_runtime,
    }


def get_task_info_contract_data():
    return __get_contract_data(__TASK_INFO_CONTRACT_FILE_NAME)


def get_make_deal_contract_data():
    return __get_contract_data(__MAKE_DEAL_CONTRACT_FILE_NAME)


def get_executing_contract_data():
    return __get_contract_data(__EXECUTION_CONTRACT_FILE_NAME)


def get_judgment_contract_data():
    return __get_contract_data(__JUDGMENT_CONTRACT_FILE_NAME)


def get_erc20_contract_data():
    contract_keyword = "@openzeppelin/contracts/token/ERC20/ERC20.sol:ERC20"
    return __get_contract_data(__ERC20_CONTRACT_FILE_NAME, contract_keyword)


def get_executors_storage_contract_data():
    return __get_contract_data(__EXECUTORS_STORAGE_CONTRACT_FILE_NAME)


__CONTRACTS_FOLDER = Path(__file__).resolve().parent.parent.parent / "contracts"
__CONTRACT_COMPILED_DATA = __CONTRACTS_FOLDER / "compiled.json"

__TASK_INFO_CONTRACT_FILE_NAME = "TaskInfo.sol"
__MAKE_DEAL_CONTRACT_FILE_NAME = "MakeDeal.sol"
__EXECUTION_CONTRACT_FILE_NAME = "Execution.sol"
__JUDGMENT_CONTRACT_FILE_NAME = "Judgment.sol"
__ERC20_CONTRACT_FILE_NAME = "YARPCoin.sol"
__EXECUTORS_STORAGE_CONTRACT_FILE_NAME = "ExecutorsStorage.sol"


def __get_contract_data(file_name, contract_kw: str = None):
    if contract_kw is None:
        contract_kw = f"{file_name}:{file_name[:-4]}"
    compiled_data = __get_compiled_data()
    compiled_contract = compiled_data[contract_kw]
    return compiled_contract["abi"], compiled_contract["bin"], compiled_contract["bin-runtime"]


def __get_compiled_data():
    with open(__CONTRACT_COMPILED_DATA, 'r') as f:
        compiled_data = json.load(f)
    return compiled_data


def to_bytes(hash: str) -> bytes:
    if hash.startswith("0x"):
        hash = hash[2:]
    return bytes.fromhex(hash)


def build_tx(transactable, sender: str) -> typing.Dict:
    tx = transactable.build_transaction({
        "from": sender,
        "nonce": W3.eth.get_transaction_count(sender),
        "gasPrice": W3.eth.gas_price,
        "gas": DEFAULT_GAS_AMOUNT,
        "chainId": W3.eth.chain_id,
    })
    estimated_gas = W3.eth.estimate_gas(tx, "latest")
    tx["gas"] = estimated_gas
    return tx


def get_contract_address(tx_hash: str) -> str:
    tx_receipt = W3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt.contractAddress


def sign_tx_by_company(tx):
    signed = W3.eth.account.sign_transaction(tx, COMPANY_PK)
    tx_hash = W3.eth.send_raw_transaction(signed.rawTransaction)
    tx_receipt = W3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt
