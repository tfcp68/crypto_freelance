// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";


contract TonCoin is ERC20 {
    constructor() ERC20("TonCoin", "TON") {
        uint256 mult = 10;
        for (uint i = 0; i < decimals(); ++i) {
            mult *= 10;
        }
        _mint(address(tx.origin), 1000000000000 * mult);
    }

    function decimals() public view virtual override returns (uint8) {
        return 8;
    }
}
