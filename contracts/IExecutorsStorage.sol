// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "./utils.sol";

interface IExecutorsStorage {
    function getExecutors() external view returns (utils.ExecutorData[] memory);

    function getNumExecutors() external view returns (uint);

    function wasResponded(address executor_address) external view returns (bool);

    function wasChosen(address executor_address) external view returns (bool);

    function addExecutor(address executor_address) external;

    function chooseExecutors(address[] memory chosen_executors) external;

    function returnDepositToRespondedExecutors(address exclude, uint256 deposit, IERC20 token) external;
}