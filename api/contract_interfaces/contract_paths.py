from pathlib import Path

CONTRACTS_DIR = Path(__file__).resolve().parent.parent.parent / "contracts"

MAKE_DEAL_CONTRACT_PATH = CONTRACTS_DIR / "MakeDeal.sol"
EXECUTING_CONTRACT_PATH = CONTRACTS_DIR / "Executing.sol"
JUDGMENT_CONTRACT_PATH = CONTRACTS_DIR / "Judgment.sol"
