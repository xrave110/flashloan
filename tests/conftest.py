import pytest
from brownie import (
    config,
    network,
    web3,
    accounts,
    interface,
    Router,
    FlashloanV2,
    ETH_ADDRESS,
)
from apis.rounter_v2_api import Routerv2Api
from apis.arbitrage_api import Arbitrage
from apis.curve_api import Curve

NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["hardhat", "development", "ganache"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS + [
    "mainnet-fork",
    "binance-fork",
    "matic-fork",
]
AMOUNT_1 = 49


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


# @pytest.fixture(autouse=True)
# def setup(fn_isolation):
#     """
#     Isolation setup fixture.

#     This ensures that each test runs against the same base environment.
#     """
#     pass


@pytest.fixture(scope="module")
def uniRouter(main_account):
    """Router instance with uniswap address"""
    router_v2_address = config["networks"][network.show_active()]["uniswap_router_v2"]
    yield Routerv2Api(
        account=main_account,
        router_v2=interface.IUniswapV2Router02(router_v2_address),
    )


@pytest.fixture(scope="module")
def uniRouter_1(account_1):
    """Router instance with uniswap address and second account"""
    router_v2_address = config["networks"][network.show_active()]["uniswap_router_v2"]
    yield Routerv2Api(
        account=account_1,
        router_v2=interface.IUniswapV2Router02(router_v2_address),
    )


@pytest.fixture(scope="module")
def sushiRouter(main_account):
    """Router instance with sushiswap address"""
    router_v2_address = config["networks"][network.show_active()]["sushiswap_router_v2"]
    yield Routerv2Api(
        account=main_account,
        router_v2=interface.IUniswapV2Router02(router_v2_address),
    )


@pytest.fixture(scope="module")
def curve(main_account):
    """Curve finance instance"""
    curve_provider_address = config["networks"][network.show_active()]["curve_provider"]
    yield Curve(
        account=main_account,
        provider_address=curve_provider_address,
    )


@pytest.fixture(scope="module")
def amount():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        yield int(web3.toWei(10, "ether"))
    else:
        yield int(web3.toWei(0.5, "ether"))


@pytest.fixture(scope="module")
def aave_lending_pool_v1(Contract):
    """
    Yield a `Contract` object for the Aave lending pool address provider.
    """
    yield Contract("0x24a42fD28C976A61Df5D00D0599C34c4f90748c8")


@pytest.fixture(scope="module")
def aave_lending_pool_v2():
    """
    Yield a Address of lending pool object for the Aave lending pool address provider.
    """
    yield config["networks"][network.show_active()]["aave_lending_pool_v2"]


# Mainnet reserve token fixtures - addresses are taken from
# https://docs.aave.com/developers/v/1.0/deployed-contracts/deployed-contract-instances#reserves-assets


@pytest.fixture(scope="module")
def PRICE_FEEDS():
    yield {
        "DAI_WETH": config["networks"][network.show_active()]["dai_eth_price_feed"],
        "ETH_USD": config["networks"][network.show_active()]["eth_usd_price_feed"],
        "USDC_WETH": config["networks"][network.show_active()]["usdc_eth_price_feed"],
    }


@pytest.fixture(scope="module")
def eth_usd_price(PRICE_FEEDS):
    price_feed = interface.AggregatorV3Interface(PRICE_FEEDS["ETH_USD"])
    latest_price = float(web3.fromWei(price_feed.latestRoundData()[1], "ether"))
    print(latest_price)
    yield latest_price * (10 ** 10)  # 18 Decimals


@pytest.fixture(scope="module")
def dai_weth_price(PRICE_FEEDS):
    price_feed = interface.AggregatorV3Interface(PRICE_FEEDS["DAI_WETH"])
    latest_price = float(web3.fromWei(price_feed.latestRoundData()[1], "ether"))
    print(latest_price)
    yield latest_price


@pytest.fixture(scope="module")
def usdc_weth_price(PRICE_FEEDS):
    price_feed = interface.AggregatorV3Interface(PRICE_FEEDS["USDC_WETH"])
    latest_price = float(web3.fromWei(price_feed.latestRoundData()[1], "ether"))
    print(latest_price)
    yield latest_price


@pytest.fixture(scope="module")
def get_weth(WETH, main_account, amount):
    "Get weth fixture for account 0"
    amount = amount * 1.2
    initial_balance = web3.fromWei(WETH.balanceOf(main_account), "ether")
    if initial_balance < amount:
        tx = WETH.deposit({"from": main_account, "value": amount})
        tx.wait(1)
        print(
            "Received {} WETH to account {}".format(
                int(web3.fromWei(amount, "ether")), main_account
            )
        )
        return WETH.balanceOf(main_account)


@pytest.fixture(scope="module")
def get_weth_1(WETH, account_1):
    """Get weth fixture for account 1"""
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        amount = AMOUNT_1
        initial_balance = web3.fromWei(WETH.balanceOf(account_1), "ether")
        if initial_balance < amount:
            tx = WETH.deposit({"from": account_1, "value": amount * (10 ** 18)})
            tx.wait(1)
            print("Received {} WETH to account {}".format(amount, account_1))
            return WETH.balanceOf(account_1)


@pytest.fixture(scope="module")
def create_arbitrage_opportunity(
    WETH, DAI, PRICE_FEEDS, dai_weth_price, get_weth_1, uniRouter_1
):
    """Creates arbitrage opportunity by swapping significant amount of ETH with account 1"""
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        initial_dai_balance = DAI.balanceOf(uniRouter_1.account)
        amount = web3.toWei(AMOUNT_1, "ether")
        uniRouter_1.approve_erc20(amount, uniRouter_1.router_v2.address, WETH.address)
        uniRouter_1.swap(WETH.address, DAI.address, dai_weth_price, amount)
        final_dai_balance = DAI.balanceOf(uniRouter_1.account)
        print(
            "{} < {}".format(
                initial_dai_balance + ((1 / dai_weth_price) * amount * 0.9),
                final_dai_balance,
            )
        )
        assert (
            initial_dai_balance + ((1 / dai_weth_price) * amount * 0.9)
            < final_dai_balance
        )


@pytest.fixture(scope="module")
def uni_sushi_arbitrage_obj(uniRouter, sushiRouter, WETH, DAI, PRICE_FEEDS, get_weth):
    uni_sushi_arbitrage_obj = Arbitrage(
        uniRouter,
        sushiRouter,
        WETH.address,
        DAI.address,
        PRICE_FEEDS["DAI_WETH"],
        PRICE_FEEDS["ETH_USD"],
    )
    yield uni_sushi_arbitrage_obj


@pytest.fixture(scope="module")
def DAI():
    yield interface.IERC20(config["networks"][network.show_active()]["dai"])


@pytest.fixture(scope="module")
def WETH():
    yield interface.WethInterface(config["networks"][network.show_active()]["weth"])


@pytest.fixture(scope="module")
def USDC():
    yield interface.IERC20(config["networks"][network.show_active()]["usdc"])


@pytest.fixture(scope="module")
def ETH():
    yield ETH_ADDRESS


@pytest.fixture(scope="module")
def router_sol(main_account):
    yield Router.deploy({"from": main_account})


@pytest.fixture(scope="module")
def flashloan_uni_sushi_weth_dai(
    WETH,
    DAI,
    main_account,
    uni_sushi_arbitrage_obj,
    create_arbitrage_opportunity,
    aave_lending_pool_v2,
):
    [dex1_quote, dex2_quote] = uni_sushi_arbitrage_obj.check_pools()
    if dex1_quote > dex2_quote:
        print(
            "Dex1 has more expensive {} (cheaper {})".format(
                uni_sushi_arbitrage_obj.tokenA_symbol,
                uni_sushi_arbitrage_obj.tokenB_symbol,
            )
        )
        yield FlashloanV2.deploy(
            aave_lending_pool_v2,
            WETH.address,
            DAI.address,
            uni_sushi_arbitrage_obj.dex1.router_v2.address,
            uni_sushi_arbitrage_obj.dex2.router_v2.address,
            {"from": main_account},
        )
    else:
        print(
            "Dex2 has more expensive {} (cheaper {})".format(
                uni_sushi_arbitrage_obj.tokenA_symbol,
                uni_sushi_arbitrage_obj.tokenB_symbol,
            )
        )
        yield FlashloanV2.deploy(
            aave_lending_pool_v2,
            WETH.address,
            DAI.address,
            uni_sushi_arbitrage_obj.dex2.router_v2.address,
            uni_sushi_arbitrage_obj.dex1.router_v2.address,
            {"from": main_account},
        )


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
