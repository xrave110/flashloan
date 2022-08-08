from brownie import exceptions
from brownie import Contract, interface

ASSET_TYPE_MAPPING = {
    "0": "USD",
    "1": "BTC",
    "2": "ETH",
    "3": "StableSwap",
    "4": "CryptoSwap",
}


class Curve:
    def __init__(self, provider_address):
        self.provider = Contract.from_explorer(provider_address)
        self.registry = Contract.from_explorer(self.provider.get_registry())
        self.swaps = Contract.from_explorer(self.provider.get_address(2))

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


def main():
    crv = Curve("0x0000000022D53366457F9d5E68Ec105046FC4383")
    crv.get_all_pool_names_and_tokens()
