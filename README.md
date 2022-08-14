# Flashloans with brownie and pytest

## Brief explanation of fundamentals
Most of the decentralized exchanges (DEXes) rely on automatic market makers (AMM) which differs from traditional order book existing on centralized exchanges (CEXes). Traditional order book is just batch of sell and buy orders which meet at some point between the lowest sell and highest buy order. When somebody is able to accept current price in order book the transaction happens. AMM however uses user's liquidity to trading assets and allow users to trade their crypto directly on-chain through smart contracts without giving control of their private keys. Uniswap (first DEX) allowed anyone to be "market maker" by providing liquidity. Liquidity providers get LP-tokens (usually ERC20 tokens) which reflects their share in the pool. So user's can be some kind of cantors by providing liquidity and having some rewards from cantor's clients who exchange tokens. One of the most important feature is fact that the price in AMM concept is not dynamicaly updated like in traditional order book model. It creates the opportunity to arbitrage and what is more, the arbitrage is usually the only thing which keeps the prices of multiple tokens pegged with CEXes once the liquidity depth is violated. 
## Arbitrages on dexes
In order to buy cheaper token on one dex and sell it on another, you must know the AMM formula and reserves of certain pool. The simplest example is formula invented by Uniswap k = x * y, where k is a constant and x,y may vary as the reserves in pool changes due to swaps. When the change happens, there is need to find another exhange where the reserves keeps the previous ratio. There is a wide range of dexes to choose.  

## New innovations introduced by Sushiswap, Curve and Balancer

The Uniswap AMM idea has been improving by different protocols. Each protocol introduces a new innovations related to AMMs. The first one is Sushiswap that was created basing on uniswap idea. The main innovation here was the dex token can be farmed by liquidity providers. Later the Sushiswap has choosen a little different way than Uniswap introducing lending and borrowing solutions and trying to be on every important EVM blockchain. Another dex is a Curve which improved swapping between stablecoins by flattening the uniswap "x*y=k" curve in the area where the most swaps happens. [image]
Moreover the curve has a little different approach to pools architecture and is written in different technologies than other dexes (mainly Python and Vyper instead of Javascript and Solidity). The Curve is also more transparent and offers very interesting governance functionality for farming their token CRV.
The last but not least protocol is a Balancer that as the first protocol allowed to provide more than 2 tokens (up to 8) into the liquidity.


## Dexes pros and cons
Dexes advantages:
User control the funds, anonymous, no cetral entity which could be hacked

Drawbacks:
Not easy to use,
Usually lower liquidity,
Vulnerability of smart contracts
## How flashloan works ?

## How pytest works and what are the fixtures ?

## Router class

## Arbitrage class

## Brownie config

## Conftest preparation

## Tests

## Pytest CLI (debugging)

## Flashloan Smart Contract

## Final Tests

## Flashloan repo

### Content
- scripts and tests are written for:
  - [x] mainnet-fork 
  - [ ] kovan testnet
  - [ ] mainnet
  - [ ] mumbai
  - [ ] polygon
- [x] interfaces to uniswap routerv2, aave and aave flashloans
- [x] scripts which allow to get weth, create uniswap pool for arbitrage opportunity
- [x] scripts and tests which allow to perform flashloans
- [x] solidity smart contract which allow to perform flashloan + scripts and tests for it


