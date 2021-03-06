# NOTE: The following tests begin by transferring assets to the deployed flashloan
# contract. this ensures that the tests pass with the base Flashloan implementation,
# i.e. one that does not implement any custom logic.

# The initial transfer should be removed prior to testing your final implementation.
from brownie import accounts, web3
from brownie import FlashloanV2, interface, accounts  # temporary
import pytest
import pdb


def test_eth_dai_swap(WETH, DAI, PRICE_FEEDS, get_weth, uniRouter):
    """"""
    pytest.skip()
    initial_dai_balance = DAI.balanceOf(uniRouter.account)
    amount = web3.toWei(0.05, "ether")
    uniRouter.approve_erc20(amount, uniRouter.router_v2.address, WETH.address)
    price = uniRouter.get_asset_price(PRICE_FEEDS["DAI_WETH"])
    uniRouter.swap(WETH.address, DAI.address, price, amount)
    final_dai_balance = DAI.balanceOf(uniRouter.account)
    print(
        "{} < {}".format(
            initial_dai_balance + ((1 / price) * amount * 0.9), final_dai_balance
        )
    )

    assert initial_dai_balance + ((1 / price) * amount * 0.9) < final_dai_balance


@pytest.fixture()
def test_provide_eth_dai_liquidity(WETH, DAI, PRICE_FEEDS, get_weth, uniRouter):
    """"""
    initial_dai_balance = DAI.balanceOf(uniRouter.account)
    amount = web3.toWei(0.05, "ether")
    price = uniRouter.get_asset_price(PRICE_FEEDS["DAI_WETH"])
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


def test_arbitrage(WETH, DAI, uni_sushi_arbitrage_obj, create_arbitrage_opportunity):
    initial_eth_balance = WETH.balanceOf(uni_sushi_arbitrage_obj.router_dex1.account)
    initial_usd_balance = uni_sushi_arbitrage_obj.get_current_balances()
    final_usd_balance = uni_sushi_arbitrage_obj.perform_arbitrage(
        web3.toWei(10, "ether")
    )
    final_eth_balance = WETH.balanceOf(uni_sushi_arbitrage_obj.router_dex1.account)
    assert initial_usd_balance < final_usd_balance
    assert initial_eth_balance < final_eth_balance


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


def test_solidity_swap(WETH, DAI, PRICE_FEEDS, uniRouter, get_weth, router_sol):
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
    price = uniRouter.get_asset_price(PRICE_FEEDS["DAI_WETH"])
    print(
        "{} < {}".format(
            initial_dai_balance + ((1 / price) * amount * 0.9), final_dai_balance
        )
    )
    assert initial_dai_balance + ((1 / price) * amount * 0.9) < final_dai_balance


def test_solidity_add_liquidity(
    WETH, DAI, PRICE_FEEDS, uniRouter, get_weth, router_sol
):
    pytest.skip()
    liquidity = 0  # to imporve
    initial_dai_balance = DAI.balanceOf(uniRouter.account)
    amount = web3.toWei(0.05, "ether")
    price = uniRouter.get_asset_price(PRICE_FEEDS["DAI_WETH"])
    print(1 / price)
    required_dai_balance = price * amount + ((price * amount) * 0.09)

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


def test_arbitrage_flashloan(
    WETH,
    DAI,
    PRICE_FEEDS,
    main_account,  # TBD can be main_account instead
    get_weth,
    flashloan_uni_sushi_weth_dai,
):
    initial_weth_balance = WETH.balanceOf(main_account)
    amount_to_lend = web3.toWei(5, "ether")
    try:
        accounts[0].transfer(flashloan_uni_sushi_weth_dai.address, "0.05 ether")
    except:
        raise ("Issue with transfering funds")

    print(f"Initial WETH balance {initial_weth_balance}")
    print(
        f"ETH balance of flashloan contract: {flashloan_uni_sushi_weth_dai.balance()}"
    )

    flashloan_uni_sushi_weth_dai.makeArbitrage(
        amount_to_lend,
        {"from": main_account},
    )
    flashloan_uni_sushi_weth_dai.withdrawTokenAProfit({"from": main_account})
    final_weth_balance = WETH.balanceOf(main_account)
    # price = uniRouter.get_asset_price(PRICE_FEEDS["DAI_WETH"])
    assert initial_weth_balance < final_weth_balance
    # print(
    #     "{} < {}".format(
    #         initial_dai_balance + ((1 / price) * amount * 0.9), final_dai_balance
    #     )
    # )
    # assert initial_dai_balance + ((1 / price) * amount * 0.9) < final_dai_balance


def test_arbitrage_flashloan2(create_arbitrage_opportunity):
    aave_lending_pool_v2 = "0xB53C1a33016B2DC2fF3653530bfF1848a515c8c5"
    flashloan = FlashloanV2.deploy(
        aave_lending_pool_v2,
        "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "0x6B175474E89094C44Da98b954EedeAC495271d0F",
        "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F",
        "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
        {"from": accounts[0]},
    )

    WETH = interface.IERC20("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
    WETH.transfer(accounts[0], "1 ether", {"from": WETH.address})
    initial_weth_amount = web3.fromWei(int(WETH.balanceOf(accounts[0])), "ether")
    print(f"initial weth amount: {initial_weth_amount}")
    WETH.transfer(flashloan, "1 ether", {"from": accounts[0]})
    print(f"FLashloan and arbitrage...")
    flashloan.makeArbitrage("10 ether")
    final_weth_amount = web3.fromWei(int(WETH.balanceOf(accounts[0])), "ether")
    print(f"final weth amount: {final_weth_amount}")
