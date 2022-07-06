# NOTE: The following tests begin by transferring assets to the deployed flashloan
# contract. this ensures that the tests pass with the base Flashloan implementation,
# i.e. one that does not implement any custom logic.

# The initial transfer should be removed prior to testing your final implementation.
from brownie import interface, web3
import pytest


def test_eth_dai_swap(WETH, DAI, DAI_WETH_PRICE_FEED, get_weth, uniRouter):
    """"""
    pytest.skip()
    initial_dai_balance = DAI.balanceOf(uniRouter.account)
    amount = web3.toWei(0.05, "ether")
    uniRouter.approve_erc20(amount, uniRouter.router_v2.address, WETH.address)
    price = uniRouter.get_asset_price(DAI_WETH_PRICE_FEED)
    uniRouter.swap(WETH.address, DAI.address, price, amount)
    final_dai_balance = DAI.balanceOf(uniRouter.account)
    print(
        "{} < {}".format(
            initial_dai_balance + ((1 / price) * amount * 0.9), final_dai_balance
        )
    )

    assert initial_dai_balance + ((1 / price) * amount * 0.9) < final_dai_balance


@pytest.fixture()
def test_eth_dai_swap_1(WETH, DAI, DAI_WETH_PRICE_FEED, get_weth_1, uniRouter_1):
    """"""
    initial_dai_balance = DAI.balanceOf(uniRouter_1.account)
    amount = web3.toWei(80, "ether")
    uniRouter_1.approve_erc20(amount, uniRouter_1.router_v2.address, WETH.address)
    price = uniRouter_1.get_asset_price(DAI_WETH_PRICE_FEED)
    uniRouter_1.swap(WETH.address, DAI.address, price, amount)
    final_dai_balance = DAI.balanceOf(uniRouter_1.account)
    print(
        "{} < {}".format(
            initial_dai_balance + ((1 / price) * amount * 0.9), final_dai_balance
        )
    )

    assert initial_dai_balance + ((1 / price) * amount * 0.9) < final_dai_balance


@pytest.fixture()
def test_provide_eth_dai_liquidity(WETH, DAI, DAI_WETH_PRICE_FEED, get_weth, uniRouter):
    """"""
    initial_dai_balance = DAI.balanceOf(uniRouter.account)
    amount = web3.toWei(0.05, "ether")
    price = uniRouter.get_asset_price(DAI_WETH_PRICE_FEED)
    print(1 / price)
    required_dai_balance = price * amount

    # to be improved
    if initial_dai_balance < required_dai_balance:
        uniRouter.approve_erc20(amount, uniRouter.router_v2.address, WETH.address)
        uniRouter.swap(WETH.address, DAI.address, price, amount)

    initial_weth_balance = WETH.balanceOf(uniRouter.account)
    if initial_weth_balance < amount:
        tx = WETH.deposit({"from": uniRouter.account, "value": amount * 10 ** 18})
        tx.wait(1)

    initial_pair_liquidity = uniRouter.get_pair_liquidity(DAI.address, WETH.address)
    initial_pair_balance = uniRouter.get_pair_contract(
        DAI.address, WETH.address
    ).balanceOf(uniRouter.account)
    print("Before: {}".format(initial_pair_liquidity))
    uniRouter.addLiquidity(DAI.address, WETH.address, amount, price)
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


def test_arbitrage(WETH, DAI, uni_sushi_arbitrage_obj, test_eth_dai_swap_1):
    uni_sushi_arbitrage_obj.perform_arbitrage(web3.toWei(10, "ether"))


def test_dai_flashloan(Contract, accounts, DAI):
    """
    Test a flashloan that borrows DAI.

    To use a different asset, swap DAI with any of the fixture names in `tests/conftest.py`
    """
    pytest.skip()
    # purchase DAI on uniswap
    uniswap_dai = Contract.from_explorer("0x2a1530C4C41db0B0b2bB646CB5Eb1A67b7158667")
    uniswap_dai.ethToTokenSwapInput(
        1, 10000000000, {"from": accounts[0], "value": "2 ether"}
    )

    # transfer DAI to the flashloan contract
    balance = DAI.balanceOf(accounts[0])
    DAI.transfer(flashloan_v2, balance, {"from": accounts[0]})

    flashloan_v2.flashloan(DAI, {"from": accounts[0]})


def test_batch_eth_dai_flashloan(Contract, accounts, DAI, WETH):
    """
    Test a flashloan that borrows WETH and DAI.
    """
    pytest.skip()
    # purchase DAI on uniswap
    uniswap_dai = Contract.from_explorer("0x2a1530C4C41db0B0b2bB646CB5Eb1A67b7158667")
    uniswap_dai.ethToTokenSwapInput(
        1, 10000000000, {"from": accounts[0], "value": "2 ether"}
    )

    # transfer DAI to the flashloan contract
    balance = DAI.balanceOf(accounts[0])
    DAI.transfer(flashloan_v2, balance, {"from": accounts[0]})

    # transfer ether to the flashloan contract
    accounts[0].transfer(WETH, "2 ether")
    WETH.transfer(flashloan_v2, "2 ether", {"from": accounts[0]})

    flashloan_v2.flashloan([WETH, DAI], ["1 ether", "1 ether"], {"from": accounts[0]})
