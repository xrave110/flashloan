from brownie import exceptions
from brownie import Contract, interface, web3, accounts

ASSET_TYPE_MAPPING = {
    "0": "USD",
    "1": "BTC",
    "2": "ETH",
    "3": "StableSwap",
    "4": "CryptoSwap",
}


class Curve:
    def __init__(self, account, provider_address):
        self.provider = Contract.from_explorer(provider_address)
        self.registry = Contract.from_explorer(
            self.provider.get_registry()
        )  # https://curve.readthedocs.io/registry-registry.html
        self.swaps = Contract.from_explorer(
            self.provider.get_address(2)
        )  # https://curve.readthedocs.io/registry-exchanges.html
        self.factory = Contract.from_explorer(
            self.provider.get_address(
                3
            )  # https://curve.readthedocs.io/factory-deployer.html
        )
        self.synth_swaps = self.provider.get_address(
            5
        )  # https://curve.readthedocs.io/exchange-cross-asset-swaps.html !!!!
        self.account = account

    def approve_erc20(self, amount, to, erc20_address):
        tx_hash = None
        print("Approving ERC20...")
        erc20 = interface.IERC20(erc20_address)
        allowance = erc20.allowance(self.account, to)
        if allowance > amount:
            print("You have already allowance {} ERC20 tokens!".format(allowance))
        else:

            tx_hash = erc20.approve(to, amount, {"from": self.account})
            print("Approved!")
            tx_hash.wait(1)
        return tx_hash

    def get_all_pool_names_and_tokens(self):
        for idx in range(self.registry.pool_count()):
            pool_address = self.registry.pool_list(idx)
            pool_contract = Contract.from_explorer(pool_address)
            dict_of_coins = {}
            coins = []
            for i in range(4):
                try:
                    coins.append(pool_contract.coins(i))
                except exceptions.VirtualMachineError:
                    break
            for coin in coins:
                if "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE" == coin:
                    symbol = "ETH"
                else:
                    symbol = interface.IERC20(coin).symbol()
                dict_of_coins[symbol] = coin

            lp_token = self.registry.get_lp_token(pool_address)
            lp_name = interface.IERC20(lp_token).name()
            lp_symbol = interface.IERC20(lp_token).symbol()
            asset_type = self.registry.get_pool_asset_type(pool_address)
            print(
                f"LP token: {lp_name} ({lp_symbol})\nAsset type: {ASSET_TYPE_MAPPING[str(asset_type)]}\nDetails: {dict_of_coins}\n---------"
            )

    def get_all_metapool_names_and_tokens(self):
        for idx in range(self.factory.pool_count()):
            pool_address = self.factory.pool_list(idx)
            # pool_contract = Contract.from_explorer(pool_address)
            dict_of_coins = {}
            coins = self.factory.get_coins(pool_address)
            coins = set(
                filter(
                    lambda address: True if ("0" * 40) not in address else False,
                    coins,
                )
            )
            print(coins)
            for coin in coins:
                if "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE" == coin:
                    symbol = "ETH"
                else:
                    symbol = interface.IERC20(coin).symbol()
                dict_of_coins[symbol] = coin
                if "ETH" in symbol:
                    print(f"Pool {idx}\nDetails: {dict_of_coins}\n---------")

    def _find_pool_with_tokens(
        self, address_from_token, address_to_token, from_to_price, amount
    ):
        return (0, False)

    def swap(
        self,
        address_from_token,
        address_to_token,
        from_to_price,
        amount,
        reverse_feed=False,
    ):
        stable_swap = ""
        pool_address = self.registry.find_pool_for_coins(
            address_from_token, address_to_token
        )
        if pool_address == 0x00:

            (pool_address, found) = self._find_pool_with_tokens(
                address_from_token, address_to_token
            )
            if not found:
                raise ("Curve__Pool not found")

        else:
            stable_swap = Contract.from_explorer(pool_address)
        # (pool_address, amount_to) = self.swaps.get_best_rate(
        #     address_from_token, address_to_token, amount
        # )
        (from_idx, to_idx, exchange_underlying) = self.registry.get_coin_indices(
            pool_address, address_from_token, address_to_token
        )
        amount_to = stable_swap.get_dy(from_idx, to_idx, amount)
        if reverse_feed:
            from_to_price = 1 / from_to_price
        estimated_price = amount_to / amount
        amount_out_min = int((from_to_price * 0.90) * amount)
        print(
            f"Expected min price: {from_to_price}\t Estimated swap price: {estimated_price}"
        )
        print(
            f"Expected out amount: {amount_out_min}\t Estimated out amount: {amount_to}"
        )
        if amount_out_min > amount_to:
            raise ("Curve__Amount of out tokens is lower than expected minimum")
        (token_from, token_to, exchange_underlying,) = self.registry.get_coin_indices(
            pool_address,
            address_from_token,
            address_to_token,
        )
        if exchange_underlying:
            swap_tx = self.swaps.exchange_underlying(
                pool_address,
                address_from_token,
                address_to_token,
                amount,
                amount_out_min,
                {"from": self.account},
            )
        else:
            swap_tx = self.swaps.exchange(
                pool_address,
                address_from_token,
                address_to_token,
                amount,
                amount_out_min,
                {"from": self.account},
            )
        swap_tx.wait(1)

    def get_pair_quote(self, address_token_a, address_token_b, amount=10 ** 18):
        (pool_address, amount_to) = self.swaps.get_best_rate(
            address_token_a, address_token_b, amount
        )
        return amount_to

    def get_asset_price(self, address_price_feed, reverted=False):
        price_feed = interface.AggregatorV3Interface(address_price_feed)
        latest_price = web3.fromWei(price_feed.latestRoundData()[1], "ether")
        print(f"Price feed latest data: {latest_price}")
        return float(latest_price)


def main():
    crv = Curve(accounts[0], "0x0000000022D53366457F9d5E68Ec105046FC4383")
    # crv.get_all_pool_names_and_tokens()
    crv.get_all_metapool_names_and_tokens()
