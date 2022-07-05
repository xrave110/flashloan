import pytest
from brownie import config, network, web3, accounts, interface
from tests.rounter_v2_api import Routerv2Api

# import pdb

NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["hardhat", "development", "ganache"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS + [
    "mainnet-fork",
    "binance-fork",
    "matic-fork",
]


def check_local_blockchain_envs():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()


@pytest.fixture(scope="module")
def main_account():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        print(
            "main_account: {} Type: {}".format(
                accounts[0].address, type(accounts[0].address)
            )
        )
        return accounts[0].address

    else:
        account = accounts.add(config["wallets"]["from_key"])
        return account.address


@pytest.fixture(scope="module")
def account_1():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[1]
    else:
        return accounts.add(config["wallets"]["from_key1"])


def init_re(dex_type):
    weth_address = config["networks"][network.show_active()]["weth"]
    dai_address = config["networks"][network.show_active()]["dai"]
    router_v2 = config["networks"][network.show_active()][dex_type]
    contract = interface.IUniswapV2Router02(router_v2)


@pytest.fixture(autouse=True)
def setup(fn_isolation):
    """
    Isolation setup fixture.

    This ensures that each test runs against the same base environment.
    """
    pass


# @pytest.fixture(scope="module")
# def flashloan_v2():
#     yield run_flashloan()


@pytest.fixture(scope="module")
def uniRouter(main_account):
    router_v2_address = config["networks"][network.show_active()]["uniswap_router_v2"]
    yield Routerv2Api(
        account=main_account,
        router_v2=interface.IUniswapV2Router02(router_v2_address),
    )


@pytest.fixture(scope="module")
def sushiRouter(main_account):
    router_v2_address = config["networks"][network.show_active()]["sushiswap_router_v2"]
    yield Routerv2Api(
        account=main_account,
        router_v2=interface.IUniswapV2Router02(router_v2_address),
    )


@pytest.fixture(scope="module")
def aave_lending_pool_v1(Contract):
    """
    Yield a `Contract` object for the Aave lending pool address provider.
    """
    yield Contract("0x24a42fD28C976A61Df5D00D0599C34c4f90748c8")


@pytest.fixture(scope="module")
def aave_lending_pool_v2(Contract):
    """
    Yield a `Contract` object for the Aave lending pool address provider.
    """
    yield Contract("0xB53C1a33016B2DC2fF3653530bfF1848a515c8c5")


# Mainnet reserve token fixtures - addresses are taken from
# https://docs.aave.com/developers/v/1.0/deployed-contracts/deployed-contract-instances#reserves-assets


@pytest.fixture(scope="module")
def DAI_WETH_PRICE_FEED():
    yield config["networks"][network.show_active()]["dai_eth_price_feed"]


@pytest.fixture(scope="module")
def WETH():
    yield interface.WethInterface(config["networks"][network.show_active()]["weth"])


@pytest.fixture(scope="module")
def get_weth(WETH, main_account):
    amount = 0.1
    initial_balance = web3.fromWei(WETH.balanceOf(main_account), "ether")
    if initial_balance < amount:
        tx = WETH.deposit({"from": main_account, "value": amount * 10 ** 18})
        tx.wait(1)
        print("Received {} WETH".format(amount))
        return WETH.balanceOf(main_account)

# @pytest.fixture(scope="module")
# def ETH():
#     yield "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"


@pytest.fixture(scope="module")
def DAI():
    yield interface.IERC20(config["networks"][network.show_active()]["dai"])


# @pytest.fixture(scope="module")
# def USDC(Contract):
#     yield Contract("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")


# @pytest.fixture(scope="module")
# def SUSD(Contract):
#     yield Contract("0x57Ab1ec28D129707052df4dF418D58a2D46d5f51")


# @pytest.fixture(scope="module")
# def TUSD(Contract):
#     yield Contract("0x0000000000085d4780B73119b644AE5ecd22b376")


# @pytest.fixture(scope="module")
# def USDT(Contract):
#     yield Contract("0xdAC17F958D2ee523a2206206994597C13D831ec7")


# @pytest.fixture(scope="module")
# def BUSD(Contract):
#     yield Contract("0x4Fabb145d64652a948d72533023f6E7A623C7C53")


# @pytest.fixture(scope="module")
# def BAT(Contract):
#     yield Contract("0x0D8775F648430679A709E98d2b0Cb6250d2887EF")


# @pytest.fixture(scope="module")
# def KNC(Contract):
#     yield Contract("0xdd974D5C2e2928deA5F71b9825b8b646686BD200")


# @pytest.fixture(scope="module")
# def LEND(Contract):
#     yield Contract("0x80fB784B7eD66730e8b1DBd9820aFD29931aab03")


# @pytest.fixture(scope="module")
# def LINK(Contract):
#     yield Contract("0x514910771AF9Ca656af840dff83E8264EcF986CA")


# @pytest.fixture(scope="module")
# def MANA(Contract):
#     yield Contract("0x0F5D2fB29fb7d3CFeE444a200298f468908cC942")


# @pytest.fixture(scope="module")
# def MKR(Contract):
#     yield Contract("0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2")


# @pytest.fixture(scope="module")
# def REP(Contract):
#     yield Contract("0x1985365e9f78359a9B6AD760e32412f4a445E862")


# @pytest.fixture(scope="module")
# def SNX(Contract):
#     yield Contract("0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F")


# @pytest.fixture(scope="module")
# def WBTC(Contract):
#     yield Contract("0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599")


# @pytest.fixture(scope="module")
# def ZRX(Contract):
#     yield Contract("0xE41d2489571d322189246DaFA5ebDe1F4699F498")


# @pytest.fixture(scope="module")
# def dai_eth_price_feed(Contract):
#     yield Contract("0xaEA2808407B7319A31A383B6F8B60f04BCa23cE2")