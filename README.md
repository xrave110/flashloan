# Flashloans with brownie and pytest
Most of the decentralized exchanges (DEXes) rely on automatic market makers (AMM). AMM is a type of order book which is not dynamicaly updated like in traditional order book in centralized exchanges (CEXes). It creates the opportunity to arbitrage and what is more the arbitrage is usually the only thing which keeps the prices of multiple tokens pegged with CEXes once the liquidity depth is violated.
## Arbitrages on dexes
In order to buy cheaper token on one dex and sell it on another, you must know the AMM formula and reserves of certain pool. The simplest example is formula invented by Uniswap k = x * y, where k is a constant and x,y may vary as the reserves in pool may vary due to swaps.

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


