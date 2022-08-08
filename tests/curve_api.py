from brownie import Contract

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

    def get_all_pool_names_and_tokens(self):
        for idx in range(self.registry.pool_count()):
            pool_address = self.registry.pool_list(idx)
            lp_token = self.registry.get_lp_token(pool_address)
            asset_type = self.registry.get_pool_asset_type(pool_address)
            print(
                f"LP token: {lp_token}\n Asset type: {ASSET_TYPE_MAPPING[str(asset_type)]}"
            )


crv = Curve("0x0000000022D53366457F9d5E68Ec105046FC4383")
crv.get_all_pool_names_and_tokens()
