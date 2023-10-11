// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "./IExecutorsStorage.sol";

contract ExecutorsStorage is IExecutorsStorage {
    address owner;
    utils.ExecutorData[] private executors;

    modifier onlyOwner() {
        require(msg.sender == owner);
        // , "You can't do this.");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function getExecutors() public view override returns (utils.ExecutorData[] memory) {
        return executors;
    }

    function getNumExecutors() public view override returns (uint) {
        return executors.length;
    }

    function wasResponded(address executor_address) public view override returns (bool) {
        for (uint i = 0; i < executors.length; ++i) {
            if (executors[i].executorAddress == executor_address) {
                return true;
            }
        }
        return false;
    }

    function wasChosen(address executor_address) public view override returns (bool) {
        for (uint i = 0; i < executors.length; ++i) {
            if (executors[i].executorAddress == executor_address) {
                if (executors[i].wasChosen) {
                    return true;
                }
                return false;
            }
        }
        return false;
    }

    function addExecutor(address executor_address) public override onlyOwner {
        if (wasResponded(executor_address)) {
            // revert("You're already responded.");
            revert();
        }

        utils.ExecutorData memory executor_data = utils.ExecutorData(executor_address, false);
        executors.push(executor_data);
    }

    function chooseExecutors(address[] memory chosen_executors) public override onlyOwner {
        uint chosen = 0;

        for (uint i = 0; i < chosen_executors.length; ++i) {
            bool was_chosen = chooseExecutor(chosen_executors[i]);
            if (was_chosen) {
                ++chosen;
            }
        }

        require(chosen != 0);
        // , "No chosen executors.");
    }

    function chooseExecutor(address executor_address) private returns (bool) {
        for (uint i = 0; i < executors.length; ++i) {
            if (executors[i].executorAddress == executor_address) {
                if (executors[i].wasChosen) {
                    return false;
                }
                executors[i].wasChosen = true;
                return true;
            }
        }
        return false;
    }

    function returnDepositToRespondedExecutors(address exclude, uint256 deposit, IERC20 token) public override onlyOwner {
        for (uint i = 0; i < executors.length; ++i) {
            if (executors[i].executorAddress == exclude) {
                continue;
            }
            token.transferFrom(owner, executors[i].executorAddress, deposit);
        }
    }
}