from brownie import accounts, web3
from brownie import FlashloanV2, interface, accounts  # temporary
import pytest
import pdb


def test_arbitrage(
    WETH, DAI, get_weth, amount, uni_sushi_arbitrage_obj, create_arbitrage_opportunity
):
    initial_eth_balance = WETH.balanceOf(uni_sushi_arbitrage_obj.dex1.account)
    print(f"INITIAL: {initial_eth_balance}")
    initial_usd_balance = uni_sushi_arbitrage_obj.get_current_balances()
    final_usd_balance = uni_sushi_arbitrage_obj.perform_arbitrage(amount)
    final_eth_balance = WETH.balanceOf(uni_sushi_arbitrage_obj.dex1.account)
    print(f"FINAL: {final_eth_balance}")
    assert initial_usd_balance < final_usd_balance
    assert initial_eth_balance < final_eth_balance