from api.contract_interfaces import COMPANY_ACCOUNT_ADDRESS

import datetime

MINIMAL_JUDGMENT_TIME = datetime.timedelta(minutes=1)

# TOKEN_NAME = "YARP"
# TOKEN_DECIMALS = 2

MARKETPLACE_FEE_PERCENT = 1

MAKE_DEAL_CONTRACT_SIGN_TYPE = 1
EXECUTION_CONTRACT_SIGN_TYPE = 2
JUDGMENT_CONTRACT_SIGN_TYPE = 3
DEFAULT_TRANSACTION_SIGN_TYPE = 4
ACCEPT_SOLUTION_SIGN_TYPE = 5

CONTRACT_TYPES = [
    ('m', 'MakeDeal'),
    ('e', 'Executing'),
    ('j', 'Judgment'),
]

TIME_CONSTANTS = {
    'h': "hour",
    'M': 'minute',
    'd': 'day',
    'w': "week",
    'm': "month",
}

TIME_CONSTANT_TO_MULT = {
    "M": 60,
    "h": 60 * 60,
    "d": 60 * 60 * 24,
    "w": 60 * 60 * 24 * 7,
    "m": 60 * 60 * 24 * 30
}
