// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "./ITaskInfo.sol";
import "./IMakeDeal.sol";
import "./IExecution.sol";
import "./Judgment.sol";

/*

ERRORS:

0x1 = You're not executor.
0x2 = Execution finished.
0x3 = You're not customer.
0x4 = Execution not finished.
0x5 = Execution already started.
0x6 = Execution not started.
0x7 = No solutions.

*/

contract Execution is IExecution {
    event TimeExtended(uint timestamp, uint executionTimeEnd);
    event ExecutionStarted(uint timeLeft);
    event SolutionUpdated(uint timestamp);
    event ExecutionFinished(uint timestamp); // при досрочном завершении работы исполнителем
    event Closed(bool isAccepted, address judgmentContractAddress); // если суда нет, то адрес равен 0x0

    modifier executorFunctionsModifier() {
        require(msg.sender == ITaskInfo(taskInfoContractAddress).getExecutor(), "0x1");
        //, "You're not executor.");
        require(!executionFinishedState, "0x2");
        //, "Execution finished.");
        _;
    }

    modifier customerFunctionsModifier() {
        require(msg.sender == ITaskInfo(taskInfoContractAddress).getCustomer(), "0x3");
        //, "You're not customer.");
        _;
    }

    modifier executionFinished() {
        require(executionFinishedState || block.timestamp > executionTimeEnd, "0x4");
        //, "Execution not finished.");
        _;
    }

    address private makeDealContractAddress;
    address private taskInfoContractAddress;

    uint private executionTimeEnd = 0;

    bool private executionFinishedState = false; // исполнитель считает, что выполнил работу
    bool private closed = false; // true = контракт завершён; false = не завершён
    bool private accepted = false; // true = работа принята заказчиком; false = суд

    constructor(
        address task_info_contract_address
    ) {
        makeDealContractAddress = msg.sender;
        taskInfoContractAddress = task_info_contract_address;
        executionTimeEnd = block.timestamp + ITaskInfo(task_info_contract_address).getTaskExecutionTime();
        emit ExecutionStarted(executionTimeEnd);
    }

    // executor functional

    //    function startExecution() public executorFunctionsModifier {
    //        require(executionTimeEnd == 0, "0x5");
    //        //, "Execution already started.");
    //
    //        ITaskInfo task_info_contract = ITaskInfo(taskInfoContractAddress);
    //
    //        executionTimeEnd = block.timestamp + task_info_contract.getTaskExecutionTime();
    //        emit ExecutionStarted(executionTimeEnd);
    //    }

    function finishExecution() public executorFunctionsModifier {
        require(ITaskInfo(taskInfoContractAddress).getSolution().length != 0, "0x7");
        executionFinishedState = true;
        executionTimeEnd = block.timestamp;
        emit ExecutionFinished(block.timestamp);
    }

    function addSolution(
        uint256 solution_id,
        bytes32 solution_sha256hashsum
    ) public executorFunctionsModifier {
        require(executionTimeEnd != 0, "0x6");

        utils.SolutionData memory solution_data = utils.SolutionData(
            solution_id,
            solution_sha256hashsum,
            block.timestamp
        );
        ITaskInfo(taskInfoContractAddress).addSolution(solution_data);
        emit SolutionUpdated(block.timestamp);
    }

    // customer functional

    function addExecutionTime(uint additional_time) public customerFunctionsModifier {
        ITaskInfo task_info = ITaskInfo(taskInfoContractAddress);
        task_info.addTaskExecutionTime(additional_time);

        if (executionTimeEnd == 0) {
            return;
        }

        if (block.timestamp < executionTimeEnd) {
            // если выполнение начато, но ещё не завершено
            executionTimeEnd += additional_time;
            return;
        }

        // если время вышло
        executionTimeEnd = block.timestamp + additional_time;
        emit TimeExtended(block.timestamp, executionTimeEnd);
    }

    function acceptSolution() public customerFunctionsModifier executionFinished {
        executionFinishedState = true;
        closed = true;
        accepted = true;

        payExecutorForWork();

        emit Closed(accepted, address(0x0));
    }

    function payExecutorForWork() private {
        IERC20 token = getToken();
        uint256 all_balance = token.balanceOf(address(this));
        address executor = ITaskInfo(taskInfoContractAddress).getExecutor();
        token.transfer(executor, all_balance);
    }

    function denySolution(uint judgment_time) public customerFunctionsModifier executionFinished {
        executionFinishedState = true;
        closed = true;
        accepted = false;

        createJudgmentContract(judgment_time);
    }

    function createJudgmentContract(uint judgment_time) private {
        Judgment judgment_contract = new Judgment(
            taskInfoContractAddress,
            judgment_time
        );

        IERC20 token = getToken();

        uint256 all_balance = token.balanceOf(address(this));
        token.transfer(address(judgment_contract), all_balance);

        ITaskInfo(taskInfoContractAddress).grantPublicAccess();
        ITaskInfo(taskInfoContractAddress).setNewMasterSmartContract(address(judgment_contract));

        emit Closed(accepted, address(judgment_contract));
    }

    // public functional

    function getExecutionTimeEnd() public view returns (uint) {
        require(executionTimeEnd != 0, "0x6");
        //, "Execution not started.");
        return executionTimeEnd;
    }

    function getMakeDealContractAddress() public view override returns (address) {
        return makeDealContractAddress;
    }

    function getTaskInfoContractAddress() public view override returns (address) {
        return taskInfoContractAddress;
    }

    function close() public {
        // завершает выполнение контракта, если время вышло
        require(!executionFinishedState && block.timestamp > executionTimeEnd);
        executionFinishedState = true;
        returnRewardToCustomerIfNoSolution();
        emit ExecutionFinished(executionTimeEnd);
    }

    function returnRewardToCustomerIfNoSolution() private {
        ITaskInfo task_info_contract = ITaskInfo(taskInfoContractAddress);
        if (task_info_contract.getSolution().length != 0)
            return;

        IERC20 token = getToken();

        address customer = task_info_contract.getCustomer();
        uint256 balance = token.balanceOf(address(this));
        token.transfer(customer, balance);
    }

    function getToken() private view returns (IERC20) {
        return ITaskInfo(taskInfoContractAddress).getToken();
    }
}
