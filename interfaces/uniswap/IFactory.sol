// SPDX-License-Identifier: MIT license
pragma solidity >=0.6.2;

interface IFactory {
    function getPair(address tokenA, address tokenB)
        external
        view
        returns (address pair);
}
