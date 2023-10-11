// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "./utils.sol";

interface ITaskInfo {
    function getTokenAddress() external view returns (address);

    function getToken() external view returns (IERC20);

    function getCustomer() external view returns (address);

    function getTaskData() external view returns (utils.TaskData memory);

    function getTaskExecutionTime() external view returns (uint);

    function getPrice() external view returns (uint256);

    function getSecurityDeposit() external view returns (uint256);

    function getExecutor() external view returns (address);

    function getSolution() external view returns (utils.SolutionData[] memory);

    function setNewMasterSmartContract(address new_master) external;

    function addTaskExecutionTime(uint additional_time) external;

    function setExecutor(address executor_) external;

    function addSolution(utils.SolutionData memory solution_data) external;

    function grantPublicAccess() external;
}