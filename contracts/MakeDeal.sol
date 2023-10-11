// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "./IMakeDeal.sol";
import "./ExecutorsStorage.sol";
import "./Execution.sol";
import "./TaskInfo.sol";

/*
ERRORS:

0x1 = Security deposit part not in [1, 99].
0x2 = Contract already activated.
0x3 = Not enough allowance.
0x4 = Contract not activated.
0x5 = Contract closed.
0x6 = Not customer.
0x7 = No chosen executors.
0x8 = You not chosen.
0x9 = Customer can't do that.

*/

contract MakeDeal is IMakeDeal {
    event Closed(address executionContractAddress);

    address private taskInfoContractAddress;
    address private executorsStorageContractAddress;

    bool activated = false;
    bool closed = false;

    constructor(
        address token,
        uint256 task_id,
        bytes32 task_hashsum,
        uint task_execution_time,
        uint256 price,
        uint8 security_deposit_part
    ) {
        require(security_deposit_part > 0 && security_deposit_part < 100);
        //, "0x1");
        //, "Security deposit part not in [1, 99].");

        createTaskInfoContract(
            token,
            task_id,
            task_hashsum,
            task_execution_time,
            price,
            security_deposit_part
        );

        createExecutorsStorageContract();
    }

    function createTaskInfoContract(
        address token,
        uint256 task_id,
        bytes32 task_hashsum,
        uint task_execution_time,
        uint256 price,
        uint8 security_deposit_part
    ) private {
        utils.TaskData memory task_data = utils.TaskData(
            task_id,
            task_hashsum,
            block.timestamp
        );

        uint256 security_deposit = price * security_deposit_part / 100;

        TaskInfo task_info_contract = new TaskInfo(
            token,
            tx.origin,
            task_data,
            task_execution_time,
            price,
            security_deposit
        );

        taskInfoContractAddress = address(task_info_contract);
    }

    function createExecutorsStorageContract() private {
        ExecutorsStorage executors_storage = new ExecutorsStorage();
        executorsStorageContractAddress = address(executors_storage);
    }

    function getTaskInfoContractAddress() public view override returns (address) {
        return taskInfoContractAddress;
    }

    function getExecutorsStorageContractAddress() public view returns (address) {
        return executorsStorageContractAddress;
    }

    function isActivated() public view returns (bool) {
        return activated;
    }

    function countMoneyDistribution() public view returns (uint256, uint256, uint256) {
        // @return price, security_deposit, marketplace_fee
        uint256 price = ITaskInfo(taskInfoContractAddress).getPrice();
        uint256 security_deposit = ITaskInfo(taskInfoContractAddress).getSecurityDeposit();
        return (
            price,
            security_deposit,
            price * 100 / 99 - price
        );
    }

    function activate() public {
        require(!activated);
        //, "0x2");
        //, "Contract already activated.");

        uint256 price;
        uint256 security_deposit;
        uint256 marketplace_fee;
        IERC20 token = getToken();

        (price, security_deposit, marketplace_fee) = countMoneyDistribution();
        uint256 allowance = token.allowance(msg.sender, address(this));
        require(allowance >= price + marketplace_fee);
        //, "0x3");
        //, "Not enough allowance.");

        token.transferFrom(msg.sender, utils.COMPANY_ADDRESS, marketplace_fee);
        token.transferFrom(msg.sender, address(this), price);
        activated = true;
    }

    function respond() public {
        checkActivatedAndNotClosed();
        ITaskInfo task_info_contract = ITaskInfo(taskInfoContractAddress);
        require(msg.sender != task_info_contract.getCustomer());
        //, "0x9");
        //, "Customer can't do that.");

        IERC20 token = getToken();

        uint256 sender_allowance = token.allowance(msg.sender, address(this));
        uint256 security_deposit = task_info_contract.getSecurityDeposit();
        require(sender_allowance >= security_deposit);
        //, "0x3");
        //, "Not enough allowance.");

        token.transferFrom(msg.sender, address(this), security_deposit);

        IExecutorsStorage(executorsStorageContractAddress).addExecutor(msg.sender);
    }

    function chooseExecutors(address[] memory chosen_executors) public {
        checkActivatedAndNotClosed();
        require(msg.sender == ITaskInfo(taskInfoContractAddress).getCustomer());
        //, "0x6");
        //, "Not customer.");

        IExecutorsStorage(executorsStorageContractAddress).chooseExecutors(chosen_executors);
    }

    function acceptInvitation() public {
        if (!IExecutorsStorage(executorsStorageContractAddress).wasChosen(msg.sender)) {
            // revert("You're not chosen.");
            revert();
        }

        closed = true;
        ITaskInfo(taskInfoContractAddress).setExecutor(msg.sender);

        returnSecurityDepositsToRespondedExecutors(msg.sender);
        createExecutionContract();
    }

    function returnSecurityDepositsToRespondedExecutors(address exclude) private {
        IExecutorsStorage executors_storage_contract = IExecutorsStorage(executorsStorageContractAddress);
        uint num_executors = executors_storage_contract.getNumExecutors() - 1;
        uint256 security_deposit = ITaskInfo(taskInfoContractAddress).getSecurityDeposit();

        IERC20 token = getToken();

        token.approve(address(executors_storage_contract), security_deposit * num_executors);
        executors_storage_contract.returnDepositToRespondedExecutors(exclude, security_deposit, token);
    }

    function createExecutionContract() private {
        Execution execution_contract = new Execution(getTaskInfoContractAddress());

        IERC20 token = getToken();

        uint256 all_balance = token.balanceOf(address(this));
        token.transfer(address(execution_contract), all_balance);

        ITaskInfo(taskInfoContractAddress).setNewMasterSmartContract(address(execution_contract));

        emit Closed(address(execution_contract));
    }

    function checkActivatedAndNotClosed() private view {
        require(activated);
        //, "0x4");
        //, "Contract not activated.");
        require(!closed);
        //, "0x5");
        //, "Contract closed.");
    }

    function getToken() private view returns (IERC20) {
        return ITaskInfo(taskInfoContractAddress).getToken();
    }
}