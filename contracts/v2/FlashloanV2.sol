// SPDX-License-Identifier: MIT license
pragma solidity ^0.6.6;

import "./aave/FlashLoanReceiverBaseV2.sol";
import "../../interfaces/v2/ILendingPoolAddressesProviderV2.sol";
import "../../interfaces/v2/ILendingPoolV2.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@uniswap/v2-periphery@1.0.0-beta.0/contracts/interfaces/IUniswapV2Router02.sol";

contract FlashloanV2 is FlashLoanReceiverBaseV2 {
    address public addressTokenA;
    address public addressTokenB;
    address public tokenACheaperRouterAddress;
    address public tokenBCheaperRouterAddress;
    address private owner;

    constructor(
        address _addressProvider,
        address _addressTokenA,
        address _addressTokenB,
        address _tokenACheaperRouterAddress,
        address _tokenBCheaperRouterAddress
    ) public FlashLoanReceiverBaseV2(_addressProvider) {
        addressTokenA = _addressTokenA;
        addressTokenB = _addressTokenB;
        tokenACheaperRouterAddress = _tokenACheaperRouterAddress;
        tokenBCheaperRouterAddress = _tokenBCheaperRouterAddress;
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "You are not an owner");
        _;
    }

    function swapTokens(
        address _addressFromToken,
        address _addressToToken,
        address _routerAddress,
        uint256 _amount,
        address _to
    ) public returns (uint256) {
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
        uint256[] memory tokenBought = routerContract.swapExactTokensForTokens(
            _amount,
            0,
            path,
            _to,
            deadline
        );
        return tokenBought[0];
    }

    /*
     * Start the arbitrage
     */
    function makeArbitrage(uint256 amount) public onlyOwner {
        bytes memory data = "";
        address[] memory tokens = new address[](1);
        uint256[] memory amounts = new uint256[](1);
        IERC20 token = IERC20(addressTokenA);
        tokens[0] = addressTokenA;
        amounts[0] = amount;
        flashloan(tokens, amounts);

        // Any left amount of DAI is considered profit
        uint256 profit = token.balanceOf(address(this));
        // Sending back the profits
        require(
            token.transfer(msg.sender, profit),
            "Could not transfer back the profit"
        );
    }

    /**
     * @dev This function must be called only be the LENDING_POOL and takes care of repaying
     * active debt positions, migrating collateral and incurring new V2 debt token debt.
     *
     * @param assets The array of flash loaned assets used to repay debts.
     * @param amounts The array of flash loaned asset amounts used to repay debts.
     * @param premiums The array of premiums incurred as additional debts.
     * @param initiator The address that initiated the flash loan, unused.
     * @param params The byte array containing, in this case, the arrays of aTokens and aTokenAmounts.
     */
    function executeOperation(
        address[] calldata assets,
        uint256[] calldata amounts,
        uint256[] calldata premiums,
        address initiator,
        bytes calldata params
    ) external override returns (bool) {
        //
        // This contract now has the funds requested.
        // Your logic goes here.
        require(
            addressTokenA == assets[0],
            "There is a difference between asset addresses"
        );
        uint256 amount = amounts[0];
        uint256 deadline = now + 3000;
        IERC20 fromToken = IERC20(addressTokenA);
        require(fromToken.balanceOf(address(this)) > 0, "There is no tokenA");
        fromToken.approve(addressTokenA, amounts[0]);
        swapTokens(
            addressTokenA,
            addressTokenB,
            tokenACheaperRouterAddress,
            amount,
            address(this)
        );
        uint256 balanceOfTokenB = IERC20(addressTokenB).balanceOf(
            address(this)
        );
        require(balanceOfTokenB > 0, "There is no tokenB");
        uint256 tokenABought = swapTokens(
            addressTokenB,
            addressTokenA,
            tokenBCheaperRouterAddress,
            balanceOfTokenB,
            address(this)
        );

        // At the end of your logic above, this contract owes
        // the flashloaned amounts + premiums.
        // Therefore ensure your contract has enough to repay
        // these amounts.

        // Approve the LendingPool contract allowance to *pull* the owed amount
        // for (uint256 i = 0; i < assets.length; i++) {
        //     uint256 amountOwing = amounts[i].add(premiums[i]);
        //     IERC20(assets[i]).approve(address(LENDING_POOL), amountOwing);
        // }

        //repay loans
        uint256 totalDebt = amount + premiums[0];
        IERC20(assets[0]).approve(address(LENDING_POOL), totalDebt);
        require(tokenABought > totalDebt, "Did not profit");

        return true;
    }

    function _flashloan(address[] memory assets, uint256[] memory amounts)
        internal
    {
        address receiverAddress = address(this);

        address onBehalfOf = address(this);
        bytes memory params = "";
        uint16 referralCode = 0;

        uint256[] memory modes = new uint256[](assets.length);

        // 0 = no debt (flash), 1 = stable, 2 = variable
        for (uint256 i = 0; i < assets.length; i++) {
            modes[i] = 0;
        }

        LENDING_POOL.flashLoan(
            receiverAddress,
            assets,
            amounts,
            modes,
            onBehalfOf,
            params,
            referralCode
        );
    }

    /*
     *  Flash multiple assets
     */
    function flashloan(address[] memory assets, uint256[] memory amounts)
        public
        onlyOwner
    {
        _flashloan(assets, amounts);
    }

    /*
     *  Flash loan 1000000000000000000 wei (1 ether) worth of `_asset`
     */
    // function flashloan(address _asset) public onlyOwner {
    //     bytes memory data = "";
    //     uint256 amount = 1 ether;

    //     address[] memory assets = new address[](1);
    //     assets[0] = _asset;

    //     uint256[] memory amounts = new uint256[](1);
    //     amounts[0] = amount;

    //     _flashloan(assets, amounts);
    // }

    // this functionality has FlashLoanReceiverBaseV2 - receive() external payable {}

    function withdraw(uint _amount) public onlyOwner {
        payable(msg.sender).transfer(_amount);
    }

    function withdrawTokenAProfit() public onlyOwner {
        IERC20 tokenA = IERC20(addressTokenA);
        uint256 tokenABalance = tokenA.balanceOf(address(this));
        require(tokenABalance > 0, "There is no tokenA");
        tokenA.transferFrom(address(this), msg.sender, tokenABalance);
    }
}
