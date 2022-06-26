from brownie import FlashloanV2, accounts, config, network, interface
from scripts.helpful_scripts import (
    get_account,
    approve_erc20,
    price_feed_mapping,
    get_asset_price,
)
from scripts.deployment_v2 import deploy_flashloan
from scripts.get_weth import get_weth
from brownie import Contract, network, config, chain, interface
from time import time
import brownie
from web3 import Web3


MINIMUM_FLASHLOAN_WETH_BALANCE = 500000000000000000
ETHERSCAN_TX_URL = "https://kovan.etherscan.io/tx/{}"


def run_flashloan():
    """
    Executes the funcitonality of the flash loan.
    """
    account = get_account()
    print("Getting Flashloan contract...")
    flashloan = deploy_flashloan()
    weth = get_weth()
    weth.transfer(flashloan, "0.1 ether", {"from": accounts[0]})
    print("Executing Flashloan...account: {}, weth address: {}".format(account, weth))
    tx = flashloan.flashloan(weth, {"from": account})
    if network.show_active() in ["kovan"]:
        print("You did it! View your tx here: " + ETHERSCAN_TX_URL.format(tx.txid))
    return flashloan


def main():
    run_flashloan()
