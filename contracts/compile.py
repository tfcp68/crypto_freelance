from solcx import compile_files, install_solc
import json

SOLC_VERSION = "0.8.17"

install_solc(SOLC_VERSION)

compiled_data = compile_files(
    source_files=[
        "USDT.sol",
        "TonCoin.sol",
        "TaskInfo.sol",
        "MakeDeal.sol",
        "Execution.sol",
        "Judgment.sol",
        "ExecutorsStorage.sol",
    ],
    optimize=True,
    optimize_runs=200,
    output_values=["abi", "bin", "bin-runtime"],
    solc_version=SOLC_VERSION
)

with open("compiled.json", 'w') as f:
    json.dump(compiled_data, f)
