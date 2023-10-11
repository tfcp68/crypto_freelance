import web3
import os
from .constants import COMPANY_PK

__ENDPOINT = os.environ.get("WEB3_ENDPOINT", None)
assert __ENDPOINT is not None, "Web3 endpoint not provided"
__provider = web3.HTTPProvider(__ENDPOINT)

W3 = web3.Web3(__provider)
COMPANY = web3.Account.from_key(COMPANY_PK)
W3.eth.default_account = COMPANY.address
