// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "./ITaskInfo.sol";

/*

ERRORS:

0x1 = Executor not set.
0x2 = You're not contract member.
0x3 = Executor already set.
0x4 = Only master contract can call this.

*/

contract TaskInfo is ITaskInfo {
    address private masterSmartContractAddress;
    // адрес смарт контракта,
    // который может изменять данный смарт контракт

    address private tokenAddress;
    // валюта контракта

    address private customer;

    utils.TaskData private taskData;
    uint private taskExecutionTime;

    uint256 private price;
    uint256 private securityDeposit;

    address executor = address(0x0);

    utils.SolutionData[] solution;

    bool publicAccess = false;

    constructor(
        address token,
        address customer_,
        utils.TaskData memory task_data,
        uint task_execution_time,
        uint256 price_,
        uint256 security_deposit
    ) {
        masterSmartContractAddress = msg.sender;
        tokenAddress = token;
        customer = customer_;
        taskData = task_data;
        taskExecutionTime = task_execution_time;
        price = price_;
        securityDeposit = security_deposit;
    }

    function getTokenAddress() public view override returns (address) {
        return tokenAddress;
    }

    function getToken() public view override returns (IERC20) {
        return IERC20(tokenAddress);
    }

    function getCustomer() public view override returns (address) {
        return customer;
    }

    function getTaskData() public view override returns (utils.TaskData memory) {
        return taskData;
    }

    function getTaskExecutionTime() public view override returns (uint) {
        return taskExecutionTime;
    }

    function getPrice() public view override returns (uint256) {
        return price;
    }

    function getSecurityDeposit() public view override returns (uint256) {
        return securityDeposit;
    }

    function getExecutor() public view override returns (address) {
        if (executor == address(0x0)) {
            // revert("Executor not set.");
            revert("0x1");
        }
        return executor;
    }

    function getSolution() public view override returns (utils.SolutionData[] memory) {
        require(tx.origin == customer || tx.origin == executor || publicAccess, "0x2");
        //, "You're not contract member.");
        return solution;
    }

    function setNewMasterSmartContract(address new_master) external override {
        checkSender();
        masterSmartContractAddress = new_master;
    }

    function addTaskExecutionTime(uint additional_time) external override {
        checkSender();
        taskExecutionTime += additional_time;
    }

    function setExecutor(address executor_) external override {
        checkSender();
        if (executor != address(0x0)) {
            // revert("Executor already set.");
            revert("0x3");
        }
        executor = executor_;
    }

    function addSolution(utils.SolutionData memory solution_data) external override {
        checkSender();
        solution.push(solution_data);
    }

    function grantPublicAccess() external override {
        checkSender();
        publicAccess = true;
    }

    function checkSender() private view {
        require(msg.sender == masterSmartContractAddress, "0x4");
        //, "Only master contract can call this.");
    }
}