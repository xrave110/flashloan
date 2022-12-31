from brownie import accounts, web3
from brownie import FlashloanV2, interface, accounts  # temporary
import pytest
import pdb


def test_eth_dai_swap_uniswap(
    WETH, DAI, PRICE_FEEDS, get_weth, uniRouter, dai_weth_price
):
    """"""
    initial_dai_balance = DAI.balanceOf(uniRouter.account)
    amount = web3.toWei(0.05, "ether")
    uniRouter.approve_erc20(amount, uniRouter.router_v2.address, WETH.address)
    uniRouter.swap(WETH.address, DAI.address, dai_weth_price, amount)
    final_dai_balance = DAI.balanceOf(uniRouter.account)
    print(
        "{} < {}".format(
            initial_dai_balance + ((1 / dai_weth_price) * amount * 0.9),
            final_dai_balance,
        )
    )

    assert (
        initial_dai_balance + ((1 / dai_weth_price) * amount * 0.9) < final_dai_balance
    )


def test_eth_dai_swap_sushiswap(
    WETH, DAI, PRICE_FEEDS, get_weth, sushiRouter, dai_weth_price
):
    """"""
    initial_dai_balance = DAI.balanceOf(sushiRouter.account)
    amount = web3.toWei(0.05, "ether")
    sushiRouter.approve_erc20(amount, sushiRouter.router_v2.address, WETH.address)
    sushiRouter.swap(WETH.address, DAI.address, dai_weth_price, amount)
    final_dai_balance = DAI.balanceOf(sushiRouter.account)
    print(
        "{} < {}".format(
            initial_dai_balance + ((1 / dai_weth_price) * amount * 0.9),
            final_dai_balance,
        )
    )

    assert (
        initial_dai_balance + ((1 / dai_weth_price) * amount * 0.9) < final_dai_balance
    )


def test_eth_dai_swap_curve(ETH, DAI, PRICE_FEEDS, get_weth, curve, dai_weth_price):
    """"""
    initial_dai_balance = DAI.balanceOf(curve.account)
    amount = web3.toWei(0.05, "ether")
    # curve.approve_erc20(amount, curve.swaps.address, ETH.address)
    curve.swap(ETH, DAI.address, dai_weth_price, amount)
    final_dai_balance = DAI.balanceOf(curve.account)
    print(
        "{} < {}".format(
            initial_dai_balance + ((1 / dai_weth_price) * amount * 0.9),
            final_dai_balance,
        )
    )

    assert (
        initial_dai_balance + ((1 / dai_weth_price) * amount * 0.9) < final_dai_balance
    )


def test_eth_usdc_swap_curve(ETH, USDC, PRICE_FEEDS, get_weth, curve, usdc_weth_price):
    """"""
    initial_usdc_balance = USDC.balanceOf(curve.account)
    amount = web3.toWei(0.05, "ether")
    # curve.approve_erc20(amount, curve.swaps.address, ETH.address)
    curve.swap(ETH, USDC.address, usdc_weth_price, amount)
    final_usdc_balance = USDC.balanceOf(curve.account)
    print(
        "{} < {}".format(
            initial_usdc_balance + ((1 / usdc_weth_price) * amount * 0.9),
            final_usdc_balance,
        )
    )

    assert (
        initial_usdc_balance + ((1 / usdc_weth_price) * amount * 0.9)
        < final_usdc_balance
    )


def test_weth_usdc_swap_curve(
    WETH, USDC, PRICE_FEEDS, get_weth, curve, usdc_weth_price
):
    """"""
    initial_usdc_balance = USDC.balanceOf(curve.account)
    amount = web3.toWei(0.05, "ether")
    swaps_address = curve.provider.get_address(2)
    curve.approve_erc20(amount, swaps_address, WETH.address)
    print("Swapping {} to {}".format(WETH.address, USDC.address))
    curve.swap(WETH.address, USDC.address, usdc_weth_price, amount)
    final_usdc_balance = USDC.balanceOf(curve.account)
    print(
        "{} < {}".format(
            initial_usdc_balance + ((1 / usdc_weth_price) * amount * 0.9),
            final_usdc_balance,
        )
    )

    assert (
        initial_usdc_balance + ((1 / usdc_weth_price) * amount * 0.9)
        < final_usdc_balance
    )


def test_solidity_swap_uniswap(
    WETH, DAI, PRICE_FEEDS, uniRouter, get_weth, dai_weth_price, router_sol
):
    initial_dai_balance = DAI.balanceOf(uniRouter.account)
    amount = web3.toWei(0.05, "ether")
    allowance = WETH.allowance(uniRouter.account, router_sol.address)
    print(initial_dai_balance)
    if allowance < amount:
        WETH.approve(router_sol.address, amount, {"from": uniRouter.account})
    router_sol.swapTokens(
        WETH.address,
        DAI.address,
        uniRouter.router_v2.address,
        amount,
        uniRouter.account,
        {"from": uniRouter.account},
    )
    final_dai_balance = DAI.balanceOf(uniRouter.account)
    print(
        "{} < {}".format(
            initial_dai_balance + ((1 / dai_weth_price) * amount * 0.9),
            final_dai_balance,
        )
    )
    assert (
        initial_dai_balance + ((1 / dai_weth_price) * amount * 0.9) < final_dai_balance
    )
