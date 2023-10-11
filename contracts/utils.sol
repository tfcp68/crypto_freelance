// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

library utils {
//    IERC20 constant public TOKEN = IERC20(address(0x0741fB496E58A1Fbc8cb9Ef9E096393e62582613));
    address constant public COMPANY_ADDRESS = address(0x1dF62f291b2E969fB0849d99D9Ce41e2F137006e);
    uint8 constant public COMPANY_FEE_PERCENT = 1;
    uint256 constant public PRICE_THRESHOLD = 10000; // 100 YARP
    uint constant public MIN_JUDGMENT_TIME = 1 minutes - 1;

    struct ExecutorData {
        address executorAddress;
        bool wasChosen;
    }

    struct TaskData {
        uint256 id;
        bytes32 sha256hashsum;
        uint timestamp;
    }

    struct SolutionData {
        uint256 id;
        bytes32 sha256hashsum;
        uint timestamp;
    }

    struct JudgeVote {
        uint256 id;
        bytes32 sha256hashsum;
        uint timestamp;
        bool verdict; // true = поддержать претензии; false = отклонить
        address judgeAddress;
    }

    struct Argument {
        uint256 id;
        bytes32 sha256hashsum;
        uint timestamp;
    }
}