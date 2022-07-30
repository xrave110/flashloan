// SPDX-License-Identifier: MIT license
pragma solidity ^0.6.6;

import "@uniswap/v2-periphery@1.0.0-beta.0/contracts/interfaces/IUniswapV2Router02.sol";
import "@uniswap/v2-core@1.0.0/contracts/interfaces/IUniswapV2Factory.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@uniswap/v2-periphery@1.0.0-beta.0/contracts/libraries/UniswapV2Library.sol";

contract Router {
    /*address DAI = 0x;
    address WETH = 0x;
    address USDC = 0x;
    address UNI = 0x;*/

    constructor() public {}

    function swapTokens(
        address _addressFromToken,
        address _addressToToken,
        address _routerAddress,
        uint256 _amount,
        address _to
    ) public {
        require(
            uint256(
                IERC20(_addressFromToken).allowance(msg.sender, address(this))
            ) >= _amount,
            "Not enough allowance"
        );
        IERC20(_addressFromToken).transferFrom(
            msg.sender,
            address(this),
            _amount
        );
        IERC20(_addressFromToken).approve(_routerAddress, _amount);
        address[] memory path;
        path = new address[](2);
        path[0] = _addressFromToken;
        path[1] = _addressToToken;
        uint256 deadline = block.timestamp + 120;
        IUniswapV2Router02 routerContract = IUniswapV2Router02(_routerAddress);
        routerContract.swapExactTokensForTokens(
            _amount,
            0,
            path,
            _to,
            deadline
        );
    }

    /* NOT WORKING YET 
    function provideLiquidity(
        address _addressTokenA,
        address _addressTokenB,
        address _routerAddress,
        uint256 _amount
    ) public returns (uint256) {
        IERC20 tokenAContract = IERC20(_addressTokenA);
        IERC20 tokenBContract = IERC20(_addressTokenB);
        IUniswapV2Router02 routerContract = IUniswapV2Router02(_routerAddress);
        address factoryAddress = routerContract.factory();
        (uint256 reserveA, uint256 reserveB) = UniswapV2Library.getReserves(
            factoryAddress,
            _addressTokenA,
            _addressTokenB
        );
        uint256 amountB = _amount * (reserveB / reserveA);
        require(
            (tokenAContract.allowance(msg.sender, address(this)) >= _amount),
            "No allowance for token A"
        );
        require(
            (tokenBContract.allowance(msg.sender, address(this)) >= amountB),
            "No allowance for token B"
        );
        tokenAContract.transferFrom(msg.sender, address(this), _amount);
        tokenBContract.transferFrom(msg.sender, address(this), amountB);
        tokenAContract.approve(_routerAddress, _amount);
        tokenBContract.approve(_routerAddress, amountB);

        uint256 deadline = block.timestamp + 120;
        routerContract.addLiquidity(
            _addressTokenA,
            _addressTokenB,
            _amount,
            amountB,
            1,
            1,
            address(this),
            deadline
        );
        address pair = IUniswapV2Factory(factoryAddress).getPair(
            _addressTokenA,
            _addressTokenB
        );
        uint256 liquidity = IERC20(pair).balanceOf(address(this));
        return liquidity;
    }

    function removeLiquidity(
        address _addressTokenA,
        address _addressTokenB,
        address _routerAddress
    ) external {
        IUniswapV2Router02 routerContract = IUniswapV2Router02(_routerAddress);
        address factoryAddress = routerContract.factory();
        address pair = IUniswapV2Factory(factoryAddress).getPair(
            _addressTokenA,
            _addressTokenB
        );

        uint liquidity = IERC20(pair).balanceOf(address(this));
        IERC20(pair).approve(_routerAddress, liquidity);

        (uint amountA, uint amountB) = IUniswapV2Router02(_routerAddress)
            .removeLiquidity(
                _addressTokenA,
                _addressTokenB,
                liquidity,
                1,
                1,
                address(this),
                block.timestamp
            );
    }*/
}
