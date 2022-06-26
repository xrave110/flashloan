from scripts.helpful_scripts import (
    get_account,
    approve_erc20,
    price_feed_mapping,
    get_asset_price,
)
from scripts.get_weth import get_weth
from brownie import Contract, network, config, chain, interface
from time import time
import brownie
from web3 import Web3
import pdb

"""
def dai_swap_v1():
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


class Routerv2Api:
    def __init__(self, amount_to_swap, dex_type, *args):
        self.amount_to_swap = amount_to_swap
        self.account = get_account()
        self.weth_address = config["networks"][network.show_active()]["weth"]
        self.dai_address = config["networks"][network.show_active()]["dai"]
        self.router_v2 = config["networks"][network.show_active()][dex_type]
        self.contract = interface.IUniswapV2Router02(self.router_v2)
        self.liquidityTokens = self.get_pair_liquidity(
            self.dai_address, self.weth_address
        )

    def getPair(self, address_token_a, address_token_b):
        factory_address = self.contract.factory()
        factory = Contract.from_explorer(factory_address)
        pair_address = factory.getPair(address_token_a, address_token_b)
        pair = Contract.from_explorer(pair_address)
        return pair

    def update_amount_to_swap(self, amount_to_swap):
        self.amount_to_swap = amount_to_swap

    def dai_swap_v2(self):
        balance_of_dai = interface.IERC20(self.dai_address).balanceOf(
            self.account.address
        )
        balance_of_weth = interface.IERC20(self.weth_address).balanceOf(
            self.account.address
        )
        balance_of_dai_real = Web3.fromWei(balance_of_dai, "ether")
        balance_of_weth_real = Web3.fromWei(balance_of_weth, "ether")

        print(
            f"The starting balance of DAI in {self.account.address} is now {balance_of_dai_real}"
        )
        print(
            f"The starting balance of ETH in {self.account.address} is now {balance_of_weth_real}"
        )

        if network.show_active() in ["mainnet-fork"]:
            get_weth()

        approve_erc20(
            self.amount_to_swap, self.router_v2, self.weth_address, self.account
        )
        approve_erc20(
            self.amount_to_swap,
            self.router_v2,
            self.dai_address,
            self.account,
        )

        price_feed_address = price_feed_mapping[network.show_active()][
            (self.dai_address, self.weth_address)
        ]
        self.swap(
            self.weth_address,
            self.dai_address,
            self.amount_to_swap,
            self.account,
            price_feed_address,
            reverse_feed=True,
        )
        dai_balance = Web3.fromWei(
            interface.IERC20(self.dai_address).balanceOf(self.account.address), "ether"
        )
        print(
            f"The ending balance of DAI in {self.account.address} is now {dai_balance}"
        )

    def provide_liquidity_dai_eth(self):

        if network.show_active() in ["mainnet-fork"]:
            get_weth()
            price_feed_address = price_feed_mapping[network.show_active()][
                (self.dai_address, self.weth_address)
            ]
            tx = approve_erc20(
                self.amount_to_swap,
                self.router_v2,
                self.weth_address,
                self.account,
            )
            tx = approve_erc20(
                self.amount_to_swap,
                self.router_v2,
                self.dai_address,
                self.account,
            )
            self.swap(
                self.weth_address,
                self.dai_address,
                self.amount_to_swap,
                self.account,
                price_feed_address,
                reverse_feed=True,
            )

        balance_of_dai = interface.IERC20(self.dai_address).balanceOf(
            self.account.address
        )
        balance_of_weth = interface.IERC20(self.weth_address).balanceOf(
            self.account.address
        )
        balance_of_dai_real = Web3.fromWei(balance_of_dai, "ether")
        balance_of_weth_real = Web3.fromWei(balance_of_weth, "ether")
        if network.show_active() in ["kovan"]:
            amount_dai_to_add = 50 * (10 ** 18)
        else:
            amount_dai_to_add = balance_of_dai / 10

        print(
            f"The starting balance of DAI in {self.account.address} is now {balance_of_dai_real}"
        )
        print(
            f"The starting balance of ETH in {self.account.address} is now {balance_of_weth_real}"
        )

        self.addLiquidity(
            self.dai_address,
            self.weth_address,
            amount_dai_to_add,
            self.account,
            self.router_v2,
        )

        balance_of_dai = interface.IERC20(self.dai_address).balanceOf(
            self.account.address
        )
        balance_of_weth = interface.IERC20(self.weth_address).balanceOf(
            self.account.address
        )
        balance_of_dai_real = Web3.fromWei(balance_of_dai, "ether")
        balance_of_weth_real = Web3.fromWei(balance_of_weth, "ether")
        print(
            f"The ending balance of DAI in {self.account.address} is now {balance_of_dai_real}"
        )
        print(
            f"The ending balance of ETH in {self.account.address} is now {balance_of_weth_real}"
        )

    def swap(
        self,
        address_from_token,
        address_to_token,
        amount,
        account,
        price_feed_address,
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
        print(
            "Amount: {} amountOutMin: {}".format(
                Web3.fromWei(amount, "ether"), Web3.fromWei(amountOutMin, "ether")
            )
        )
        timestamp = chain[brownie.web3.eth.get_block_number()]["timestamp"] + 120
        swap_tx = self.contract.swapExactTokensForTokens(
            amount, 0, path, account.address, timestamp, {"from": account}
        )
        swap_tx.wait(1)
        return swap_tx

    def addLiquidity(
        self,
        address_token_a,
        address_token_b,
        amount_a_desired,
        account,
        router_address,
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
        print("Approved {} of token a".format(amount_a_desired))
        tx = approve_erc20(
            amount_b_desired,
            router_address,
            address_token_b,
            account,
        )
        print("Approved {} of token b".format(amount_b_desired))
        timestamp = chain[brownie.web3.eth.get_block_number()]["timestamp"] + 120
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
        pair = self.getPair(address_token_a, address_token_b)
        [tokenA_reserves, tokenB_reserves, timestampReceived] = pair.getReserves()
        print(
            f"Reserves before providing liquidity {Web3.fromWei(tokenA_reserves, 'ether')} tokenA and {Web3.fromWei(tokenB_reserves, 'ether')} tokenB"
        )
        liquidity_tx = self.contract.addLiquidity(
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
        [tokenA_reserves, tokenB_reserves, timestampReceived] = pair.getReserves()
        print(
            f"Reserves after providing liquidity {Web3.fromWei(tokenA_reserves, 'ether')} tokenA and {Web3.fromWei(tokenB_reserves, 'ether')} tokenB"
        )
        print(f"You received {liquidity_tx} DAI/ETH liquidity tokens")
        return liquidity_tx

    def balance_of_dai(self):
        dai = Contract.from_explorer(config["networks"][network.show_active()]["dai"])
        retVal = dai.balanceOf(self.account)
        return float(retVal)

    def remove_liquidity_dai_eth(self):

        balance_of_dai = interface.IERC20(self.dai_address).balanceOf(
            self.account.address
        )
        balance_of_weth = interface.IERC20(self.weth_address).balanceOf(
            self.account.address
        )
        balance_of_dai_real = Web3.fromWei(balance_of_dai, "ether")
        balance_of_weth_real = Web3.fromWei(balance_of_weth, "ether")
        print(
            f"The starting balance of DAI in {self.account.address} is now {balance_of_dai_real}"
        )
        print(
            f"The starting balance of ETH in {self.account.address} is now {balance_of_weth_real}"
        )
        self.remove_liquidity(self.dai_address, self.weth_address)

    def remove_liquidity(self, address_token_a, address_token_b):
        self.liquidityTokens = self.get_pair_liquidity(address_token_a, address_token_b)
        timestamp = chain[brownie.web3.eth.get_block_number()]["timestamp"] + 120
        pair = self.getPair(address_token_a, address_token_b)
        approve_erc20(
            self.liquidityTokens, self.contract.address, pair.address, self.account
        )
        self.contract.removeLiquidity(
            address_token_a,
            address_token_b,
            self.liquidityTokens,
            0,
            0,
            self.account,
            timestamp,
            {"from": self.account},
        )
        self.liquidityTokens = self.get_pair_liquidity(address_token_a, address_token_b)

    def get_pair_liquidity(self, address_token_a, address_token_b):
        pair = self.getPair(address_token_a, address_token_b)
        [reserves_a, reserves_b, a] = pair.getReserves()
        pair_account_balance = pair.balanceOf(self.account)
        pair_total_balance = pair.totalSupply()
        factor = pair_account_balance / pair_total_balance
        # print(
        #     "Your liquidity is {}\nPair liquidity is {}\nYour Tokens: {} DAI and {} ETH\nToken Reserves: {} DAI and {} ETH\n".format(
        #         Web3.fromWei(pair_account_balance, "ether"),
        #         Web3.fromWei(pair_total_balance, "ether"),
        #         float(Web3.fromWei(reserves_a, "ether")) * factor,
        #         float(Web3.fromWei(reserves_b, "ether")) * factor,
        #         Web3.fromWei(reserves_a, "ether"),
        #         Web3.fromWei(reserves_b, "ether"),
        #     )
        # )
        return pair.balanceOf(self.account)


def main():
    # # Liquidity
    routerObjS = Routerv2Api(
        amount_to_swap=amount_to_swap, dex_type="sushiswap_router_v2"
    )
    # routerObjS.provide_liquidity_dai_eth()
    # routerObjS.remove_liquidity_dai_eth()

    routerObjS.dai_swap_v2()

    routerObj = Routerv2Api(amount_to_swap=amount_to_swap, dex_type="uniswap_router_v2")

    routerObj.dai_swap_v2()