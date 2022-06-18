from scripts.helpful_scripts import (
    get_account,
    approve_erc20,
    price_feed_mapping,
    get_asset_price,
)
from scripts.get_weth import get_weth
from brownie import Contract, network, config, chain, web3, interface
from time import time
import brownie
from web3 import Web3

"""
def dai_swap1():
    account = get_account()
    # purchase DAI on uniswap
    # uniswap_dai = Contract.from_explorer("0x2a1530C4C41db0B0b2bB646CB5Eb1A67b7158667")
    # uniswap_dai.ethToTokenSwapInput(
    #     1, 10000000000, {"from": account, "value": "1 ether"}
    # )
    uniswap_router_v1 = Contract.from_explorer(
        config["networks"][network.show_active()]["uniswap_router_v1"]
    )

    print("Uniswap router v1 -> factory: {}\n".format(uniswap_router_v1.factory()))
    tx = uniswap_router_v1.swapExactTokensForTokens(
        10 ** 17,
        5 * (10 ** 17),
        [
            config["networks"][network.show_active()]["weth"],
            config["networks"][network.show_active()]["dai"],
        ],
        account,
        {"from": account, "value": 10 ** 16},
    )
    """

amount_to_swap = Web3.toWei(0.05, "ether")


def dai_swap2():
    account = get_account()
    weth_address = config["networks"][network.show_active()]["weth"]
    dai_address = config["networks"][network.show_active()]["dai"]
    uniswap_router_v2 = config["networks"][network.show_active()]["uniswap_router_v2"]
    print(
        f"The starting balance of DAI in {account.address} is now {interface.IERC20(dai_address).balanceOf(account.address)}"
    )

    if network.show_active() in ["mainnet-fork"]:
        get_weth(account=account)

    tx = approve_erc20(amount_to_swap, uniswap_router_v2, weth_address, account)
    approve_erc20(
        amount_to_swap,
        uniswap_router_v2,
        dai_address,
        account,
    )
    tx.wait(1)

    # routerv2 = interface.IUniswapV2Router02(uniswap_router_v2)
    # print("Uniswap router v2 -> factory: {}\n".format(routerv2.factory()))
    # timestamp = chain[web3.eth.get_block_number()]["timestamp"] + 120
    # routerv2.addLiquidity(
    #     config["networks"][network.show_active()]["weth"],
    #     "0xFab46E002BbF0b4509813474841E0716E6730136",
    #     1000000000,
    #     100000000,
    #     100000,
    #     100000000,
    #     account,
    #     timestamp,
    #     {"from": account, "value": 10 ** 16, "gas_limit": 90000000},
    # )
    # amount = 10 ** 16
    # amountOutMin = 5 * (10 ** 16)
    # timestamp = chain[web3.eth.get_block_number()]["timestamp"] + 120
    # tx = routerv2.swapExactTokensForTokens(
    #     amount,
    #     amountOutMin,
    #     [
    #         config["networks"][network.show_active()]["weth"],
    #         config["networks"][network.show_active()]["dai"],
    #     ],
    #     account,
    #     time() + 60,
    #     {"from": account},
    # )

    price_feed_address = price_feed_mapping[network.show_active()][
        (dai_address, weth_address)
    ]
    swap(
        weth_address,
        dai_address,
        amount_to_swap,
        account,
        price_feed_address,
        uniswap_router_v2,
        reverse_feed=True,
    )
    print(
        f"The ending balance of DAI in {account.address} is now {interface.IERC20(dai_address).balanceOf(account.address)}"
    )


def provide_liquidity_dai_eth():
    account = get_account()
    weth_address = config["networks"][network.show_active()]["weth"]
    dai_address = config["networks"][network.show_active()]["dai"]
    uniswap_router_v2 = config["networks"][network.show_active()]["uniswap_router_v2"]

    if network.show_active() in ["mainnet-fork"]:
        get_weth()
        price_feed_address = price_feed_mapping[network.show_active()][
            (dai_address, weth_address)
        ]
        tx = approve_erc20(amount_to_swap, uniswap_router_v2, weth_address, account)
        tx.wait(1)
        tx = approve_erc20(
            amount_to_swap,
            uniswap_router_v2,
            dai_address,
            account,
        )
        tx.wait(1)
        swap(
            weth_address,
            dai_address,
            amount_to_swap,
            account,
            price_feed_address,
            uniswap_router_v2,
            reverse_feed=True,
        )

    balance_of_dai = interface.IERC20(dai_address).balanceOf(account.address)
    balance_of_weth = interface.IERC20(weth_address).balanceOf(account.address)
    balance_of_dai_real = Web3.fromWei(balance_of_dai, "ether")
    balance_of_weth_real = Web3.fromWei(balance_of_weth, "ether")
    if network.show_active() in ["kovan"]:
        amount_dai_to_add = 50 * (10 ** 18)
    else:
        amount_dai_to_add = balance_of_dai / 10

    print(
        f"The starting balance of DAI in {account.address} is now {balance_of_dai_real}"
    )
    print(
        f"The starting balance of ETH in {account.address} is now {balance_of_weth_real}"
    )

    addLiquidity(
        dai_address, weth_address, amount_dai_to_add, account, uniswap_router_v2
    )

    balance_of_dai = interface.IERC20(dai_address).balanceOf(account.address)
    balance_of_weth = interface.IERC20(weth_address).balanceOf(account.address)
    balance_of_dai_real = Web3.fromWei(balance_of_dai, "ether")
    balance_of_weth_real = Web3.fromWei(balance_of_weth, "ether")
    print(
        f"The ending balance of DAI in {account.address} is now {balance_of_dai_real}"
    )
    print(
        f"The ending balance of ETH in {account.address} is now {balance_of_weth_real}"
    )


def swap(
    address_from_token,
    address_to_token,
    amount,
    account,
    price_feed_address,
    swap_router_address,
    reverse_feed=False,
):
    path = [
        address_from_token,
        address_to_token,
    ]
    # The pool jumping path to swap your token
    from_to_price = get_asset_price(address_price_feed=price_feed_address)
    if reverse_feed:
        from_to_price = 1 / from_to_price
    # amountOutMin = int((from_to_price * 0.5) * 10 ** 18)
    # 98 is 2% slippage
    # I get a little weird with units here
    # from_to_price isn't in wei, but amount is
    amountOutMin = int((from_to_price * 0.90) * amount)
    print("Amount: {} amountOutMin: {}".format(amount, amountOutMin))
    timestamp = chain[brownie.web3.eth.get_block_number()]["timestamp"] + 120
    routerv2 = interface.IUniswapV2Router02(swap_router_address)
    swap_tx = routerv2.swapExactTokensForTokens(
        amount, amountOutMin, path, account.address, timestamp, {"from": account}
    )
    swap_tx.wait(1)
    return swap_tx


def addLiquidity(
    address_token_a, address_token_b, amount_a_desired, account, router_address
):
    try:
        price_feed_address = price_feed_mapping[network.show_active()][
            (address_token_a, address_token_b)
        ]
    except KeyError:
        raise ("No price feed for this pair of tokens !")

    price = get_asset_price(address_price_feed=price_feed_address)
    print("1 ETH is {} DAI".format(1 / price))
    amount_b_desired = price * amount_a_desired
    print(
        "So I will pool {} DAI and {} ETH".format(
            Web3.fromWei(amount_a_desired, "ether"),
            Web3.fromWei(amount_b_desired, "ether"),
        )
    )
    if network.show_active() in ["kovan"]:
        amount_a_min = (
            0  # estimations must be done in different way (not from chainlink)
        )
        amount_b_min = 0
    else:
        amount_a_min = 0.9 * amount_a_desired
        amount_b_min = 0.9 * amount_b_desired

    tx = approve_erc20(amount_a_desired, router_address, address_token_a, account)
    tx.wait(1)
    print("Approved {} of token a".format(amount_a_desired))
    tx = approve_erc20(
        amount_b_desired,
        router_address,
        address_token_b,
        account,
    )
    tx.wait(1)
    print("Approved {} of token b".format(amount_b_desired))
    timestamp = chain[brownie.web3.eth.get_block_number()]["timestamp"] + 120
    routerv2 = interface.IUniswapV2Router02(router_address)
    print(
        " address_token_a: {}\n address_token_b: {}\n amount_a_desired: {}\n amount_b_desired: {}\n amount_a_min: {}\n amount_b_min: {}\n account: {}\n timestamp: {}".format(
            address_token_a,
            address_token_b,
            amount_a_desired,
            amount_b_desired,
            amount_a_min,
            amount_b_min,
            account,
            timestamp,
        )
    )
    factory = routerv2.factory()
    # uniLib = InterfaceUniswapV2Library
    reserves = routerv2.getReserves(factory, address_token_a, address_token_b)
    print(f"Reserves before providing liquidity {reserves}")
    liquidity_tx = routerv2.addLiquidity(
        address_token_a,
        address_token_b,
        amount_a_desired,
        amount_b_desired,
        amount_a_min,
        amount_b_min,
        account,
        timestamp,
        {"from": account},
    )
    liquidity_tx.wait(1)
    reserves = routerv2.getReserves(factory, address_token_a, address_token_b)
    print(f"Reserves after providing liquidity {reserves}")
    return liquidity_tx


def balance_of_dai():
    account = get_account()
    dai = Contract.from_explorer(config["networks"][network.show_active()]["dai"])
    retVal = dai.balanceOf(account)
    return float(retVal)


def main():
    # print("DAI balance for {} account: {}".format(get_account(), balance_of_dai()))
    # dai_swap1()
    # print(chain[chain.height])
    # print("DAI balance for {} account: {}".format(get_account(), balance_of_dai()))
    # dai_swap2()
    provide_liquidity_dai_eth()
    # print("DAI balance for {} account: {}".format(get_account(), balance_of_dai()))
