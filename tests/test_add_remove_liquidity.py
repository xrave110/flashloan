from brownie import accounts, web3
from brownie import FlashloanV2, interface, accounts  # temporary
import pytest
import pdb


@pytest.fixture()
def test_provide_eth_dai_liquidity(
    WETH, DAI, PRICE_FEEDS, get_weth, uniRouter, dai_weth_price
):
    """"""
    initial_dai_balance = DAI.balanceOf(uniRouter.account)
    amount = web3.toWei(0.05, "ether")
    required_dai_balance = dai_weth_price * amount

    # to be improved
    if initial_dai_balance < required_dai_balance:
        uniRouter.approve_erc20(amount, uniRouter.router_v2.address, WETH.address)
        uniRouter.swap(WETH.address, DAI.address, dai_weth_price, amount)

    initial_weth_balance = WETH.balanceOf(uniRouter.account)
    if initial_weth_balance < amount:
        tx = WETH.deposit({"from": uniRouter.account, "value": amount * 10 ** 18})
        tx.wait(1)

    initial_pair_liquidity = uniRouter.get_pair_liquidity(DAI.address, WETH.address)
    initial_pair_balance = uniRouter.get_pair_contract(
        DAI.address, WETH.address
    ).balanceOf(uniRouter.account)
    print("Before: {}".format(initial_pair_liquidity))
    uniRouter.addLiquidity(DAI.address, WETH.address, amount, dai_weth_price)
    final_pair_liquidity = uniRouter.get_pair_liquidity(DAI.address, WETH.address)
    final_pair_balance = uniRouter.get_pair_contract(
        DAI.address, WETH.address
    ).balanceOf(uniRouter.account)
    print("After: {}".format(final_pair_liquidity))
    assert final_pair_liquidity > initial_pair_liquidity
    assert final_pair_balance > initial_pair_balance


# test_provide_eth_dai_liquidity added for isolation
def test_remove_eth_dai_liquidity(WETH, DAI, uniRouter, test_provide_eth_dai_liquidity):
    """"""

    pair_contract = uniRouter.get_pair_contract(DAI.address, WETH.address)
    initial_pair_balance = pair_contract.balanceOf(uniRouter.account)

    if initial_pair_balance > 0:
        uniRouter.remove_liquidity(DAI.address, WETH.address)
        final_pair_balance = pair_contract.balanceOf(uniRouter.account)
        assert initial_pair_balance > final_pair_balance
    else:
        assert False


def test_solidity_add_liquidity(
    WETH, DAI, PRICE_FEEDS, uniRouter, get_weth, dai_weth_price, router_sol
):
    pytest.skip()
    liquidity = 0  # to imporve
    initial_dai_balance = DAI.balanceOf(uniRouter.account)
    amount = web3.toWei(0.05, "ether")
    print(1 / dai_weth_price)
    required_dai_balance = dai_weth_price * amount + ((dai_weth_price * amount) * 0.09)

    # to be improved
    if initial_dai_balance < required_dai_balance:
        amount_to_swap = amount + (amount * 0.1)
        uniRouter.approve_erc20(
            amount_to_swap, uniRouter.router_v2.address, WETH.address
        )
        uniRouter.swap(WETH.address, DAI.address, price, amount_to_swap)

    initial_weth_balance = WETH.balanceOf(uniRouter.account)
    if initial_weth_balance < amount:
        tx = WETH.deposit({"from": uniRouter.account, "value": amount * 10 ** 18})
        tx.wait(1)

    allowance = WETH.allowance(uniRouter.account, router_sol.address)
    if allowance < amount:
        WETH.approve(router_sol.address, amount, {"from": uniRouter.account})

    balance = DAI.balanceOf(uniRouter.account)
    print(f"DAI balance: {balance}")
    if allowance < required_dai_balance:
        DAI.approve(router_sol.address, balance, {"from": uniRouter.account})
    allowance = DAI.allowance(uniRouter.account, router_sol.address)
    print(f"DAI allowance: {allowance}")

    liquidity = router_sol.provideLiquidity.call(
        WETH.address,
        DAI.address,
        uniRouter.router_v2.address,
        amount,
        {"from": uniRouter.account},
    )
    print(f"Liquidity: {liquidity}")
    assert liquidity > 0