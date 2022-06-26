from brownie import FlashloanV2, config, network
from scripts.helpful_scripts import get_account

# AAVE_LENDING_POOL_ADDRESS_PROVIDER = "0xB53C1a33016B2DC2fF3653530bfF1848a515c8c5"


def deploy_flashloan():
    """
    Deploy a `FlashloanV2` contract from `accounts[0]`.
    """
    account = get_account()

    flashloan = FlashloanV2.deploy(
        config["networks"][network.show_active()]["aave_lending_pool_v2"],
        {"from": account},
    )
    return flashloan


def main():
    deploy_flashloan()