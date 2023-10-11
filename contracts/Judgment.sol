// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "./ITaskInfo.sol";
import "./IExecution.sol";

/*

ERRORS:

0x1 = Too little judgment time.
0x2 = Judgment not closed.
0x3 = You're not customer or executor.
0x4 = You didn't allow to transact security deposit.
0x5 = You can't vote.
0x6 = You already voted.
0x7 = Contract closed.
0x8 = Contract shouldn't be closed.

*/

contract Judgment {
    event ArgumentAdded(address from, uint timestamp);
    event Voted(address judge, uint timestamp);

    address private executionContractAddress;
    address private taskInfoContractAddress;

    utils.Argument[] private customerArguments;
    utils.Argument[] private executorArguments;

    utils.JudgeVote[] private judge_votes;

    uint private judgmentTimeEnd;

    bool rewardsPayed = false; // true, когда выданы награды
    uint votes_for = 0;
    uint votes_against = 0;

    constructor(
        address task_info_contract_address,
        uint judgment_time
    ) {
        require(judgment_time >= utils.MIN_JUDGMENT_TIME, "0x1");
        //, "Too little judgment time.");

        executionContractAddress = msg.sender;
        taskInfoContractAddress = task_info_contract_address;

        judgmentTimeEnd = block.timestamp + judgment_time;
    }

    function getExecutionContractAddress() public view returns (address) {
        return executionContractAddress;
    }

    function getTaskInfoContractAddress() public view returns (address) {
        return taskInfoContractAddress;
    }

    function getCustomerArguments() public view returns (utils.Argument[] memory) {
        return customerArguments;
    }

    function getExecutorArguments() public view returns (utils.Argument[] memory) {
        return executorArguments;
    }

    function getJudgmentTimeEnd() public view returns (uint) {
        return judgmentTimeEnd;
    }

    function getNumVotes() public view returns (uint) {
        return judge_votes.length;
    }

    function isClosed() public view returns (bool) {
        return rewardsPayed;
    }

    function getVotes() public view returns (utils.JudgeVote[] memory) {
        require(rewardsPayed, "0x2");
        //, "Judgment not closed.");
        return judge_votes;
    }

    function addArgument(
        uint256 argument_id,
        bytes32 argument_sha256sum
    ) public {
        checkIsContractNotClosed();
        checkCanSenderAddArguments(msg.sender);

        utils.Argument memory argument = utils.Argument(
            argument_id,
            argument_sha256sum,
            block.timestamp
        );

        address from;
        if (msg.sender == ITaskInfo(taskInfoContractAddress).getCustomer()) {
            customerArguments.push(argument);
            from = ITaskInfo(taskInfoContractAddress).getCustomer();
        }
        else {
            executorArguments.push(argument);
            from = ITaskInfo(taskInfoContractAddress).getExecutor();
        }
        emit ArgumentAdded(from, block.timestamp);
    }

    function checkCanSenderAddArguments(address sender) private view {
        require(sender == ITaskInfo(taskInfoContractAddress).getCustomer() ||
        sender == ITaskInfo(taskInfoContractAddress).getExecutor(),
            // "You're not customer or executor."
            "0x3"
        );
    }

    function vote(
        bool verdict,
        uint256 vote_id,
        bytes32 vote_sha256hashsum
    ) public {
        checkIsContractNotClosed();
        checkCanSenderVote(msg.sender);

        IERC20 token = getToken();

        uint256 security_deposit = ITaskInfo(taskInfoContractAddress).getSecurityDeposit();
        uint256 sender_allowance = token.allowance(msg.sender, address(this));
        require(sender_allowance >= security_deposit, "0x4");
        //, "You didn't allow to transact security deposit.");
        token.transferFrom(msg.sender, address(this), security_deposit);

        utils.JudgeVote memory vote_ = utils.JudgeVote(
            vote_id,
            vote_sha256hashsum,
            block.timestamp,
            verdict,
            msg.sender
        );
        judge_votes.push(vote_);
        if (verdict) {
            ++votes_for;
        }
        else {
            ++votes_against;
        }

        emit Voted(msg.sender, block.timestamp);
    }

    function checkCanSenderVote(address sender) public view {
        require(sender != ITaskInfo(taskInfoContractAddress).getCustomer() &&
        sender != ITaskInfo(taskInfoContractAddress).getExecutor(),
            // "You can't vote."
            "0x5"
        );

        for (uint i = 0; i < judge_votes.length; ++i) {
            if (judge_votes[i].judgeAddress == sender) {
                // revert("You already voted.");
                revert("0x6");
            }
        }
    }

    function checkIsContractNotClosed() private view {
        require(!rewardsPayed && block.timestamp < judgmentTimeEnd, "0x7");
        //, "Contract closed.");
    }

    function close() public {
//        checkIsContractShouldBeClosed();
        require(!rewardsPayed && block.timestamp >= judgmentTimeEnd, "0x8");

        //        uint votes_for;
        //        uint votes_against;
        //        (votes_for, votes_against) = countVotes();
        rewardsPayed = true;
        payRewards();
    }

//    function checkIsContractShouldBeClosed() private view {
//        require(!rewardsPayed && block.timestamp >= judgmentTimeEnd, "0x8");
//        //, "Contract shouldn't be closed.");
//    }

    //    function countVotes() private view returns (uint, uint) {
    //        uint votes_for = 0;
    //        uint votes_against = 0;
    //
    //        for (uint i = 0; i < judge_votes.length; ++i) {
    //            if (judge_votes[i].verdict) {
    //                ++votes_for;
    //            }
    //            else {
    //                ++votes_against;
    //            }
    //        }
    //        return (votes_for, votes_against);
    //    }

    function payRewards() private {
        //        bool winner_vote = getWinner(votes_for, votes_against);
        bool winner_vote = true;
        if (votes_against >= votes_for) {
            winner_vote = false;
        }
        payRewardToWinner(winner_vote);
        payRewardByVote(winner_vote);
        payBalanceToCompany();
    }

    //    function getWinner(uint votes_for, uint votes_against) private pure returns (bool) {
    //        // @return true = выиграл заказчик; false = выиграл исполнитель
    //        // Если количество голосов за исполнителя (votes_against) >=
    //        // количества голосов за заказчика (votes_for),
    //        // то побеждает исполнитель
    //        if (votes_against >= votes_for) {
    //            return false;
    //            // выиграл исполнитель
    //        }
    //        return true;
    // }

    function payRewardToWinner(bool winner_vote) private {
        address winner_address;
        if (winner_vote) {
            winner_address = ITaskInfo(taskInfoContractAddress).getCustomer();
        }
        else {
            winner_address = ITaskInfo(taskInfoContractAddress).getExecutor();
        }
        uint256 price = ITaskInfo(taskInfoContractAddress).getPrice();
        getToken().transfer(winner_address, price);
    }

    function payRewardByVote(bool winner_vote) private {
        // Распределение наград между судьями:
        // -- Судьи, голосовавшие за проигравшего, проигрывают ставку (в размере обеспечительного платежа)
        // -- Судьи, голосовавшие за победителя, получают свои ставки обратно,
        // а также равномерно распределяют сумму ставок судей, голосовавших за проигравшего,
        // и обеспечительный платёж проигравшего
        uint256 judge_reward = calculateJudgeReward(winner_vote);
        for (uint i = 0; i < judge_votes.length; ++i) {
            if (judge_votes[i].verdict == winner_vote) {
                getToken().transfer(judge_votes[i].judgeAddress, judge_reward);
            }
        }
    }

    function calculateJudgeReward(bool winner_vote) private view returns (uint256) {
        // Пусть A судей, голосовавших за победителя, и
        // B судей, голосовавших за проигравшего.
        // Тогда каждый судья, голосовавший за победителя, получит:
        // (B * ставка_судьи + обеспечительный_платёж_проигравшего) / A
        // или, т.к. ставка_судьи равна обеспечительному_платежу,
        // (B + 1) * обеспечительный_платёж / A
        // Также каждый судья, голосовавший за победителя,
        // получит обратно свою ставку в размере обеспечительного_платежа
        // Итог: (B + 1) * обеспечительный_платёж / A + обеспечительный_платёж
        uint256 security_deposit = ITaskInfo(taskInfoContractAddress).getSecurityDeposit();
        uint256 reward = 0;
        if (winner_vote && votes_for != 0) {
            reward = (votes_against + 1) * security_deposit / votes_for;
        }
        else if (!winner_vote && votes_against != 0) {
            reward = (votes_for + 1) * security_deposit / votes_against;
        }
        reward += security_deposit;
        return reward;
    }

    function payBalanceToCompany() private {
        // Т.к. из-за деления целых чисел на балансе контракта
        // может сохраняться некоторых остаток,
        // то этот остаток будет перечислен на адрес компании
        IERC20 token = getToken();

        uint256 all_balance = token.balanceOf(address(this));
        if (all_balance != 0) {
            token.transfer(utils.COMPANY_ADDRESS, all_balance);
        }
    }

    function getToken() private view returns (IERC20) {
        return ITaskInfo(taskInfoContractAddress).getToken();
    }
}
