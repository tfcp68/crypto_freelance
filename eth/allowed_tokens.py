from api.contract_interfaces import ERC20ContractInterface

USDT_ADDRESS = "0xAAaE1947203B90aFC537E86fe07c1FD918fd159B"
TON_ADDRESS = "0x91F502fbb4ec46b69258743F2EC65Bf8265241DA"

USDT = ERC20ContractInterface(USDT_ADDRESS)
TON = ERC20ContractInterface(TON_ADDRESS)

ALLOWED_TOKENS = [
    (USDT.address, USDT.symbol()),
    (TON.address, TON.symbol()),
]


def get_token_from_symbol(symbol: str) -> ERC20ContractInterface:
    for token_address, token_symbol in ALLOWED_TOKENS:
        if symbol == token_symbol:
            return ERC20ContractInterface(token_address)
    raise ValueError("Unknown token")
