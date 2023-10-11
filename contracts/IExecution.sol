// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

interface IExecution {
    function getMakeDealContractAddress() external view returns (address);

    function getTaskInfoContractAddress() external view returns (address);
}
