# NOTE: The following tests begin by transferring assets to the deployed flashloan
# contract. this ensures that the tests pass with the base Flashloan implementation,
# i.e. one that does not implement any custom logic.

# The initial transfer should be removed prior to testing your final implementation.
from brownie import accounts, web3
from brownie import FlashloanV2, interface, accounts  # temporary
import pytest
import pdb


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


def test_arbitrage_flashloan(
    WETH,
    DAI,
    PRICE_FEEDS,
    main_account,
    get_weth,
    eth_usd_price,
    flashloan_uni_sushi_weth_dai,
):
    # pytest.skip()
    amount = 10
    initial_weth_balance = float(
        web3.fromWei(int(WETH.balanceOf(main_account)), "ether")
    )
    initial_usd_balance = initial_weth_balance * eth_usd_price
    amount_to_lend = web3.toWei(amount, "ether")
    try:
        WETH.transfer(
            flashloan_uni_sushi_weth_dai.address, "0.5 ether", {"from": main_account}
        )
    except:
        raise ("Issue with transfering funds")

    print(f"Initial WETH balance {initial_weth_balance}")

    print(f"FLashloan with {amount} WETH and arbitrage...")
    flashloan_uni_sushi_weth_dai.makeArbitrage(amount_to_lend, {"from": main_account})
    final_weth_balance = float(web3.fromWei(int(WETH.balanceOf(main_account)), "ether"))
    final_usd_balance = final_weth_balance * eth_usd_price
    print(f"Final WETH balance {final_weth_balance}")
    print(
        "Contgratulations! You have managed to earn {} USD ({} WETH) with flashloan !".format(
            (final_usd_balance - initial_usd_balance),
            (final_weth_balance - initial_weth_balance),
        )
    )
    assert initial_weth_balance < final_weth_balance
