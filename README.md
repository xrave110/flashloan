# Flashloans with brownie and pytest #1 - DeFi fundamentals

## Brief explanation of fundamentals
Most of the decentralised exchanges (DEXes) rely on automatic market makers (AMM) which differs from traditional order book existing on centralised exchanges (CEXes). Traditional order book is just a batch of sell and buy orders which meet at some point between the lowest sell and highest buy order. When somebody is able to accept current price in order book the exchange happens. AMM however uses user’s liquidity for exchanging assets and allow users to trade their crypto directly on-chain through smart contracts without giving control of their private keys. Uniswap (first DEX) allowed anyone to be “market maker” by providing liquidity. Liquidity providers get LP-tokens (usually ERC20 tokens) which reflects their share in the pool. So user’s can be some kind of currency exhange by providing liquidity and having some rewards from currency exhange’s clients who exchange tokens. One of the most important feature is fact that the price in AMM concept is not dynamically updated like in traditional order book model. It creates the opportunity to arbitrage and what is more, the arbitrage is usually the only thing which keeps the prices of multiple tokens pegged with other exchanges once the liquidity depth is violated.

## Arbitrages on dexes
In order to buy cheaper token on one dex and sell it on another, you must be aware of the AMM formula and reserves of certain pool. The simplest example is constant product formula (reciprocal function) applied by Uniswap k = x * y, where k is a constant and x,y may vary as the reserves in pool changes due to swaps.

![Reciprocal function: (y = k / x)](./docs/imgs/ReciprocalFunction(hyperbola).png "Reciprocal function")

When the change happens, there is need to find another exchange where the reserves keeps the previous ratio. There is a wide range of dexes to choose.

## New innovations introduced by Sushiswap, Curve and Balancer
The Uniswap AMM idea has been improving by different protocols. Each protocol introduces a new innovations related to AMMs.

### Sushiswap
Sushiswap was created basing on uniswap idea. The main innovation here was the fact that dex token can be farmed by liquidity providers. Later the Sushiswap has chosen a little different way than Uniswap introducing lending and borrowing solutions and trying to be on every important EVM blockchain.
### Curve
Another dex is a Curve which improved swapping between stablecoins by flattening the uniswap hyperbola curve (x*y=k) in the area where the most swaps happens.

<img src="./docs/imgs/CurveChart.png" alt="drawing" width="300" height="210"/>

Moreover the curve has a little different approach to pools architecture and is written in different technologies than other dexes (mainly Python and Vyper instead of Javascript and Solidity). The Curve is also more transparent and offers very interesting governance functionality for farming their token CRV.

### Balancer
The last but not least protocol is a Balancer that as the first protocol allowed to provide more than 2 tokens (up to 8) into the liquidity. The price in such pool is determined by pool balances, pool weights and amounts of tokens what is called weighted maths. Moreover there was introduced something called portfolio manager and crypto index funds which allows to create synthetic index fund of certain tokens which automaticaly re-balance itself as needed. Another features are Liquidity Bootstrapping Pools (LBP) and vault. LBP give an opportunity to re-balance of certain assets of the newly created pool from LBP. LBP usually has highly trusted coin with small proportion and is used to re-balance a new pool. The vault is a kind of mapping of pools and its balances, so it keeps all pool’s balances and provide interfaces for interactions and information. Such approach allows to reduce gas spending on certain swaps and especially when routing (swaps between multiple pools in order to get expected token which is not directly available on swap) comes into place. The next improvement which goes with the vault is that the re-balancing can happen inside vault smart contract without external interaction between a pool so there is less gas usage.
## Summary: dexes pros and cons
Dexes advantages:
- User controls the funds
- Can be anonymous
- No central entity which could be hacked
- Routing
- Transparency

Drawbacks:
- Not easy to use,
- Usually lower liquidity,
- Vulnerability of smart contracts

## What is Aave and how flashloan works ?
Aave is a lending and borrowing protocol. As the name shows protocol allows to lend some crypto and get a certain interest rate from it. On the other side there are borrowers who can borrow some crypto and pay some certain interests to maintain position. Unfortunately currently there is no stable protocol which allows to borrow crypto without collateral deposit. So in order to borrow it is required to provide some kind of valuable collateral like other cryptocurrency. Because of that, borrowing is used mainly to leverage current positions or shorting certain assets. The main protocols which allows for described techniques are Compound and Aave. But aave came up with something even more crazy. They created special smart contract which utilises provided lending liquidity for borrowing cryptocurrency without any collaterals! There are of course bunch of constraints which prevents from borrowing crypto and not paying it off. The most significant constraint is the requirement to repay borrowed crypto with some interests in the same transaction. Such approach make all necessary checks related to not paying funds off possible. Flashloans are usually used for arbitrages and all transactions related to them are performed in the same transaction.

# Flashloans with brownie and pytest #2 - Toolset overview and Api development
Brownie is the most popular Python-based framework for development and testing smart contracts. 

## Brief introduction to Brownie
Brownie provides all necessary functionalities to create, deploy and test your smart contract on variety of EVM compatible networks as: local network created via ganache, testnets and mainnets. Everything  can be configured in the file called `brownie-config.yaml`. All necessary instructions to get started are on the offcial [docs website](#https://eth-brownie.readthedocs.io/en/stable/). Basic folder structure for smart contract can be created by commend: `brownie init`.

## How pytest works and what are the fixtures ?
For testing brownie uses test framework called pytest. Pytest allows to write readable tests and can be easily scaled into some more advanced test scenarios using fixtures approach. Fixtures manage test resources which can last for the certain part of test and be reused in multiple tests. It also provides typical for test frameworks setup and teardown functionalities. The usage of setup, teardown and fixtures can be showed in the special example prepared below:
- fixture.py -> takes care of setup, teardown and fixtures:
```python
''' 
@author: Kamil Palenik
@purpose: Learning - ilustrates basic features of pytest
'''
import pytest

var = "GLOBAL_VARIABLE"

@pytest.fixture(scope="module")
def fixture_module():
    print(">> START fixture_module <<")
    dictOf = {"One": 1, "Four": 4}
    yield dictOf
    print("\n>> STOP fixture_module <<")

def setup_module(module):
    """ setup any state specific to the execution of the given module."""
    print("\nSETUP -> module: {} ----------> {}".format(module.__name__, var))
    if module.__name__ == 'test_example':
        print("<if>SETUP -> module: {}".format(module.__name__))
    elif module.__name__ == 'test_example2':
        print("<elif>SETUP -> module: {}".format(module.__name__))
    else:
        print("WROOOONG")


def teardown_module(module):
    """ teardown any state that was previously setup with a setup_module
    method.
    """
    print("\nTEARDOWN -> module: {}".format(module.__name__))


@pytest.fixture(scope="function")
def fixture_function():
    print("\n>> --- START fixture_function --- <<")
    yield "function"
    print("\n>> --- STOP fixture_function --- <<")
```

Syntax explanation:
- `@pytest.fixture(scope="session/package/module/class/function")` - determine that the function below is the fixture with certain scope so it will be performed only once per session/package/module/class/function.
- `yield` - returns generator object which allows to come back to the fixture later (during teardown) and perform instructions after the yield statement.

- test_example -> the main test should be in separate files with the `test` phrase at the begining of the name:
```python
from fixture import *

def test_addition(fixture_module, fixture_function):
    print(fixture_module)
    print(fixture_function)
    assert 3+2 == 5 and fixture_function == "function"


def test_substraction(fixture_function):
    assert 3-2 == 1 and fixture_function == "function"

def test_module(fixture_module):
    assert fixture_module == {'One': 1, 'Four': 4}

```

Syntax explanation:
- `test` phrase also is required in function names in order to be tested by pytest directly.
- fixtures are passed to the test functions as the arguments, can be used in the body of the function and provides guarancy that all fixture actions before yield keyword has been done.

Once those two files are created and pytest installed according to instructions on the [offcial website](https://docs.pytest.org/en/7.1.x/#a-quick-example), the tests can be run with following command:

`pytest -sv`

After that console will show the test flow determined for setup, teardown and fixtures.

## Brownie config
`brownie-config.yaml` is powerful configuration file that allows to cofigure multiple settings. Some of this settings can be depended on network which we would like to work on. Main features:
- Managing sensitive data - it is only matter of creation .env with sensitive data and updating config file with corresponding data, example:
```yaml
dotenv: .env
wallets:
  from_key: ${PRIVATE_KEY}
  from_key1: ${PRIVATE_KEY1}
```
- Managing solidity dependencies - gives possibility to automaticaly download and import with the shorten syntax the files that are needed, example:
```yaml
dependencies:
  - OpenZeppelin/openzeppelin-contracts@3.0.0
  - Uniswap/v2-periphery@1.0.0-beta.0
  - Uniswap/v2-core@1.0.0
  - aave/protocol-v2@1.0.1
compiler:
  solc:
    remappings:
      - "@openzeppelin=OpenZeppelin/openzeppelin-contracts@3.0.0"
      - "@uniswap=Uniswap"
      - "@aave=aave/protocol-v2@1.0.1"
```
- Managing network related data - makes possible to have chain/network agnostic calls in code. All deployment and test scripts can be called with `--network <network>` parameter which determines network. Usage of construct `config['networks'][network.show_active()]['key']` makes the code network agnostic.
```yaml
networks:
  default: kovan
  mainnet-fork:
    link_token: '0x514910771af9ca656af840dff83e8264ecf986ca'
    aave_link_token: '0x514910771af9ca656af840dff83e8264ecf986ca'
    aave_lending_pool_v2: "0xB53C1a33016B2DC2fF3653530bfF1848a515c8c5"
    weth: "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    dai_eth_price_feed: "0x773616E4d11A78F511299002da57A0a94577F1f4"
    eth_usd_price_feed: "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419"
    usdc_eth_price_feed: "0x986b5E1e1755e3C2440e960477f25201B0a8bbD4"
    dai: "0x6B175474E89094C44Da98b954EedeAC495271d0F"
    usdc: "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    aave_dai_token: '0x6b175474e89094c44da98b954eedeac495271d0f'
    uniswap_router_v1: "0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45" #"0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    uniswap_router_v2: "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D" # 
    sushiswap_router_v2: "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F"
    curve_provider: "0x0000000022D53366457F9d5E68Ec105046FC4383"
    balancer_vault: "0xBA12222222228d8Ba445958a75a0704d566BF2C8"
    explorer: "https://api.etherscan.io/api"
  kovan:
    # https://aave.github.io/aave-addresses/kovan.json
    # Aave uses their own testnet tokens to ensure they are good
    # find the most up to date in the above
    aave_link_token: '0xAD5ce863aE3E4E9394Ab43d4ba0D80f419F61789'
    link_token: '0xa36085F69e2889c224210F603D836748e7dC0088'
    aave_lending_pool_v2: "0x88757f2f99175387ab4c6a4b3067c77a695b0349"
    weth: "0xd0a1e359811322d97991e03f863a0c30c2cf029c"
    aave_dai_token: '0xFf795577d9AC8bD7D90Ee22b6C1703490b6512FD'
    dai: "0x4F96Fe3b7A6Cf9725f59d353F723c1bDb64CA6Aa"
    dai_eth_price_feed: "0x22B58f1EbEDfCA50feF632bD73368b2FdA96D541"
    eth_usd_price_feed: "0x9326BFA02ADD2366b30bacB125260Af641031331"
    uniswap_router_v1: "0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45"
    uniswap_router_v2: "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    sushiswap_router_v2: "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506"
    keyhash: '0x6c3699283bda56ad74f6b855546325b68d482e983852a7a82979cc4807b641f4'
    fee: 100000000000000000
    oracle: '0x2f90A6D021db21e1B2A077c5a37B3C7E75D15b7e'
    jobId: '29fa9aa13bf1468788b7cc4a500a45b8'
```
## Api scheme
The reason for writing api class is to standarize interfaces along dexes. Despite of many differences, the main functionalities remain the same: **swap, get price determined by pool and add/remove liquidity**. All this three functionalities must be decapusalted from Dex's interfaces into the class api.
## RouterV2_Api class
The goal of router Api is to use uniswap router implementation to do calls mentioned in [Api sheme](#api-scheme). Uniswap router is the existing smart contract on the blockchain. Each of the public/external services can be easily used by our python scripts/tests. In order to use this services there is need to have ABI (Application Binary Interface) and the address of the smart contract. Brownie has a lot of useful features helping to get ABI. The most important one is the interface feature which keeps all compiled to ABI interfaces defined in interfaces folder in solidity language. The example for unsiwap router is below:
```solidity
// SPDX-License-Identifier: MIT license
pragma solidity >=0.6.2;

interface IUniswapV2Router02 {
    function factory() external pure returns (address);

    function WETH() external pure returns (address);

    function addLiquidity(
        address tokenA,
        address tokenB,
        uint256 amountADesired,
        uint256 amountBDesired,
        uint256 amountAMin,
        uint256 amountBMin,
        address to,
        uint256 deadline
    )
        external
        returns (
            uint256 amountA,
            uint256 amountB,
            uint256 liquidity
        );

    function addLiquidityETH(
        address token,
        uint256 amountTokenDesired,
        uint256 amountTokenMin,
        uint256 amountETHMin,
        address to,
        uint256 deadline
    )
        external
        payable
        returns (
            uint256 amountToken,
            uint256 amountETH,
            uint256 liquidity
        );

    function removeLiquidity(
        address tokenA,
        address tokenB,
        uint256 liquidity,
        uint256 amountAMin,
        uint256 amountBMin,
        address to,
        uint256 deadline
    ) external returns (uint256 amountA, uint256 amountB);

    function removeLiquidityETH(
        address token,
        uint256 liquidity,
        uint256 amountTokenMin,
        uint256 amountETHMin,
        address to,
        uint256 deadline
    ) external returns (uint256 amountToken, uint256 amountETH);

    function swapExactTokensForTokens(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path,
        address to,
        uint256 deadline
    ) external returns (uint256[] memory amounts);

    function swapTokensForExactTokens(
        uint256 amountOut,
        uint256 amountInMax,
        address[] calldata path,
        address to,
        uint256 deadline
    ) external returns (uint256[] memory amounts);

    function swapExactETHForTokens(
        uint256 amountOutMin,
        address[] calldata path,
        address to,
        uint256 deadline
    ) external payable returns (uint256[] memory amounts);

    function swapTokensForExactETH(
        uint256 amountOut,
        uint256 amountInMax,
        address[] calldata path,
        address to,
        uint256 deadline
    ) external returns (uint256[] memory amounts);

    function swapExactTokensForETH(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path,
        address to,
        uint256 deadline
    ) external returns (uint256[] memory amounts);

    function swapETHForExactTokens(
        uint256 amountOut,
        address[] calldata path,
        address to,
        uint256 deadline
    ) external payable returns (uint256[] memory amounts);
}
```
It is worth to mention the fact that solidity interface file can contain only such services which are supposed to be used without anything more. Once the interfaces are compiled. There is possibility to get the instance of by refering to `brownie.interface` like below:
```python
from brownie import interface
erc20 = interface.IERC20(erc20_address)
```
The instances of IERC20, AggregatorV3Interface and IFactory are used in the code in order to get the major function from [Api sheme](#api-scheme) and the main router interface is expected as an argument for the api object. All api class can be viewed [here](apis/rounter_v2_api.py).

## Curve_Api class

## Balancer_Api class

# Flashloans with brownie and pytest #3 - Arbitrage tests and flashloan implementation


## Arbitrage class

## Integration classes with arbitrage

## Conftest preparation
## Tests

## Pytest CLI (debugging)

## Flashloan Smart Contract

## Final Tests

# Flashloans with brownie and pytest #4 - Expanding to blockchains

## Expanding to new blockchain (Polygon example)

## Expanding to new blockchain (Avalanche example)
## Flashloan repo

### Content
- [ ] scripts and tests are written for:
  - [x] mainnet-fork 
  - [ ] kovan testnet
  - [ ] mainnet
  - [ ] mumbai
  - [ ] polygon
- [x] interfaces to uniswap routerv2, aave and aave flashloans
- [x] scripts which allow to get weth, create uniswap pool for arbitrage opportunity
- [x] scripts and tests which allow to perform flashloans
- [x] solidity smart contract which allow to perform flashloan + scripts and tests for it
- [ ] curve interaction
- [ ] balancer interaction


