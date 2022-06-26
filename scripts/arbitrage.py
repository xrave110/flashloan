from scripts.helpful_scripts import approve_erc20, price_feed_mapping, get_asset_price
from scripts.run_routerv2 import Routerv2Api
from scripts.run_flash_loan_v2 import run_flashloan
from scripts.get_weth import get_weth
from brownie import web3, network, interface

# import pdb

uniRouter = Routerv2Api(
    amount_to_swap=web3.toWei(0.1, "ether"), dex_type="uniswap_router_v2"
)

sushiRouter = Routerv2Api(
    amount_to_swap=web3.toWei(0.1, "ether"), dex_type="sushiswap_router_v2"
)


def check_pools():
    pair = uniRouter.getPair(uniRouter.weth_address, uniRouter.dai_address)
    [dai_reserves, weth_reserves, timestampReceived] = pair.getReserves()
    print(
        "Uniswap reserves:\n{} ETH is {} DAI ".format(
            web3.fromWei(weth_reserves, "ether"), web3.fromWei(dai_reserves, "ether")
        )
    )
    uni_quote = dai_reserves / weth_reserves
    # quote = uniRouter.contract.quote(
    #     web3.fromWei(1, "ether"), weth_reserves, dai_reserves
    # )
    # print("Uniswap:\n{} ETH is {} DAI ".format(web3.fromWei(1, "ether"), quote))

    print("Uniswap:\n1 ETH is {} DAI ".format(uni_quote))
    pair = sushiRouter.getPair(uniRouter.weth_address, uniRouter.dai_address)
    [dai_reserves, weth_reserves, timestampReceived] = pair.getReserves()
    print(
        "Sushiswap reserves:\n{} ETH is {} DAI ".format(
            web3.fromWei(weth_reserves, "ether"), web3.fromWei(dai_reserves, "ether")
        )
    )
    sushi_quote = dai_reserves / weth_reserves
    print("Sushiswap:\n1 ETH is {} DAI ".format(sushi_quote))
    # quote = uniRouter.contract.quote(
    #     web3.fromWei(1, "ether"), weth_reserves, dai_reserves
    # )
    # print("Sushiswap:\n{} ETH is {} DAI ".format(web3.fromWei(1, "ether"), quote))
    get_current_balances()
    return [uni_quote, sushi_quote]


def perform_arbitrage():
    print(">>>>>I. Before DAI swapped with ETH")
    [uni_quote, sushi_quote] = check_pools()

    if network.show_active() in ["mainnet-fork"]:
        get_weth()
    print("Gas price is {}".format(web3.eth.generate_gas_price()))
    # print("Gas limit is {}".format(web3.eth.estimate_gas()))
    if uni_quote < sushi_quote:
        print("Uniswap has cheaper ETH")
        buy_cheap(uniRouter, sushiRouter, uni_quote, sushi_quote)
    else:
        print("Sushi has cheaper ETH")
        buy_cheap(sushiRouter, uniRouter, sushi_quote, uni_quote)


def buy_cheap(cheapRouterObj, expensiveRouterObj, cheaper_quote, expensive_quote):
    protocol_fee = 0.003 * cheapRouterObj.amount_to_swap * cheaper_quote * 2
    estimated_gas_limit = 21000 * 3  # temporary hardcoded
    print("Protocol fee is: {}".format(protocol_fee))
    print()
    fees = web3.fromWei(
        (
            (web3.eth.generate_gas_price() * estimated_gas_limit * cheaper_quote)
            + protocol_fee
        ),
        "ether",
    )
    print("Total fee is: {}".format(fees))

    # if cheaper_quote + float(fees) < expensive_quote:
    print("Cheaper: {}, more expensive: {}".format(cheaper_quote, expensive_quote))
    amount_to_swap = cheapRouterObj.amount_to_swap * cheaper_quote
    if cheaper_quote < expensive_quote:
        approve_erc20(
            amount_to_swap,
            cheapRouterObj.router_v2,
            cheapRouterObj.dai_address,
            cheapRouterObj.account,
        )
        print(
            "Allowance for DAI {} \n amount to swap: {} ".format(
                float(
                    interface.IERC20(cheapRouterObj.dai_address).allowance(
                        cheapRouterObj.account, cheapRouterObj.router_v2
                    )
                ),
                amount_to_swap,
            )
        )
        price_feed_address = price_feed_mapping[network.show_active()][
            (cheapRouterObj.dai_address, cheapRouterObj.weth_address)
        ]
        print("Swapping DAI to WETH...")
        cheapRouterObj.swap(
            cheapRouterObj.dai_address,
            cheapRouterObj.weth_address,
            amount_to_swap,
            cheapRouterObj.account,
            price_feed_address,
            reverse_feed=False,
        )
        print(">>>>>II. After DAI swapped with WETH")
        get_current_balances()

        approve_erc20(
            expensiveRouterObj.amount_to_swap,
            expensiveRouterObj.router_v2,
            expensiveRouterObj.weth_address,
            expensiveRouterObj.account,
        )
        print("Swapping WETH to DAI...")
        expensiveRouterObj.swap(
            expensiveRouterObj.weth_address,
            expensiveRouterObj.dai_address,
            expensiveRouterObj.amount_to_swap,
            expensiveRouterObj.account,
            price_feed_address,
            reverse_feed=True,
        )
        print(">>>>>III. After WETH swapped with DAI")
        get_current_balances()


def get_current_balances():
    price_feed_address = price_feed_mapping[network.show_active()][
        (uniRouter.dai_address, uniRouter.weth_address)
    ]
    latest_price = get_asset_price(price_feed_address)
    weth_balance = web3.fromWei(
        interface.IERC20(uniRouter.weth_address).balanceOf(uniRouter.account), "ether"
    )
    dai_balance = web3.fromWei(
        interface.IERC20(uniRouter.dai_address).balanceOf(uniRouter.account), "ether"
    )
    print(
        ">>>> Total balance is {} DAI and {} ETH <<<<<".format(
            dai_balance, float(weth_balance)
        )
    )
    print(
        " >>>>>>>>>> Total balance in DAI: {} <<<<<<<<<<<< ".format(
            (float(weth_balance) / latest_price) + float(dai_balance)
        )
    )


def get_dai_and_weth():
    uniRouter.dai_swap_v2()
    sushiRouter.dai_swap_v2()
    get_weth()


def main():
    if network.show_active() in ["mainnet-fork"]:
        get_dai_and_weth()
    perform_arbitrage()