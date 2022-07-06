from audioop import reverse
from brownie import web3, interface


class Arbitrage:
    def __init__(
        self,
        router_dex1,
        router_dex2,
        tokenA_address,
        tokenB_address,
        address_price_feed,
    ):
        self.router_dex1 = router_dex1
        self.router_dex2 = router_dex2
        self.tokenA_address = tokenA_address
        self.tokenB_address = tokenB_address
        self.tokenA_symbol = interface.IERC20(tokenA_address).symbol()
        self.tokenB_symbol = interface.IERC20(tokenB_address).symbol()
        self.address_price_feed = address_price_feed

    def check_pools(self):
        pair_contract = self.router_dex1.get_pair_contract(
            self.tokenA_address, self.tokenB_address
        )
        [
            tokenA_reserves,
            tokenB_reserves,
            timestampReceived,
        ] = pair_contract.getReserves()
        print(
            "Dex1 reserves:\n{} {} is {} {}".format(
                web3.fromWei(tokenA_reserves, "ether"),
                self.tokenA_symbol,
                web3.fromWei(tokenB_reserves, "ether"),
                self.tokenB_symbol,
            )
        )
        dex1_quote = tokenA_reserves / tokenB_reserves
        print(
            "Dex1 :\n1 {} is {} {} ".format(
                self.tokenB_symbol, dex1_quote, self.tokenA_symbol
            )
        )
        pair_contract = self.router_dex2.get_pair_contract(
            self.tokenA_address, self.tokenB_address
        )
        [dai_reserves, weth_reserves, timestampReceived] = pair_contract.getReserves()
        print(
            "Dex2 reserves:\n{} tokenB is {} tokenA ".format(
                web3.fromWei(tokenA_reserves, "ether"),
                self.tokenA_symbol,
                web3.fromWei(tokenB_reserves, "ether"),
                self.tokenB_symbol,
            )
        )
        dex2_quote = dai_reserves / weth_reserves
        print(
            "Dex2:\n1 {} is {} {} ".format(
                self.tokenB_symbol, dex2_quote, self.tokenA_symbol
            )
        )
        self.get_current_balances()
        return [dex1_quote, dex2_quote]

    def get_current_balances(self):
        latest_price = self.router_dex1.get_asset_price(self.address_price_feed)
        tokenA_balance = web3.fromWei(
            interface.IERC20(self.tokenA_address).balanceOf(self.router_dex1.account),
            "ether",
        )
        tokenB_balance = web3.fromWei(
            interface.IERC20(self.tokenB_address).balanceOf(self.router_dex1.account),
            "ether",
        )
        print(
            ">>>> Total balance is {} {} and {} {} <<<<<".format(
                tokenA_balance,
                self.tokenA_symbol,
                float(tokenB_balance),
                self.tokenB_symbol,
            )
        )
        # TODO
        print(
            " >>>>>>>>>> Total balance in USD (WRONG!!! -> TBD): {} <<<<<<<<<<<< ".format(
                (float(tokenA_balance) / latest_price) + float(tokenB_balance)
            )
        )

    def perform_arbitrage(self, amount):
        print(
            ">>>>>I. Before {} swapped with {}".format(
                self.tokenB_symbol, self.tokenA_symbol
            )
        )
        [dex1_quote, dex2_quote] = self.check_pools()

        print("Gas price is {}".format(web3.eth.generate_gas_price()))
        # print("Gas limit is {}".format(web3.eth.estimate_gas()))
        if dex1_quote > dex2_quote:
            print(
                "Dex1 has more expensive {} (cheaper {})".format(
                    self.tokenB_symbol, self.tokenA_symbol
                )
            )
            self.buy_cheap(
                amount, self.router_dex1, self.router_dex2, dex2_quote, dex1_quote
            )

        else:
            print(
                "Dex2 has more expensive {} (cheaper {})".format(
                    self.tokenB_symbol, self.tokenA_symbol
                )
            )
            self.buy_cheap(
                amount, self.router_dex2, self.router_dex1, dex1_quote, dex2_quote
            )

    def estimate_fees(self, amount, cheap_quote):
        protocol_fee = 0.003 * amount * cheap_quote * 2
        estimated_gas_limit = 21000 * 3  # temporary hardcoded
        print("Protocol fee is: {}".format(protocol_fee))
        print()
        fees = web3.fromWei(
            (
                (web3.eth.generate_gas_price() * estimated_gas_limit * cheap_quote)
                + protocol_fee
            ),
            "ether",
        )
        print("Total fee is: {}".format(fees))
        return fees

    def buy_cheap(self, amount, cheapDex, expensiveDex, cheap_quote, expensive_quote):
        fees = self.estimate_fees(amount, cheap_quote)

        # if cheaper_quote + float(fees) < expensive_quote:
        print("Cheaper: {}, more expensive: {}".format(cheap_quote, expensive_quote))
        amount_to_swap = amount
        if cheap_quote < expensive_quote:
            cheapDex.approve_erc20(
                amount_to_swap,
                cheapDex.router_v2,
                self.tokenB_address,
            )
            # print(
            #     "Allowance for DAI {} \n amount to swap: {} ".format(
            #         float(
            #             interface.IERC20(cheapDex.dai_address).allowance(
            #                 cheapDex.account, cheapDex.router_v2
            #             )
            #         ),
            #         amount_to_swap,
            #     )
            # )

            print("Swapping {} to {}...".format(self.tokenB_symbol, self.tokenA_symbol))
            cheapDex.swap(
                self.tokenB_address,
                self.tokenA_address,
                cheap_quote,
                amount_to_swap,
                reverse_feed=True,
            )
            print(
                ">>>>>II. After {} swapped with {}".format(
                    self.tokenB_symbol, self.tokenA_symbol
                )
            )
            self.get_current_balances()
            amount_to_swap = amount * expensive_quote * 0.98
            # - float(web3.toWei(float(fees) * 1.3, "ether")
            # )  # (fees * 1.3) temporary assumption
            expensiveDex.approve_erc20(
                amount_to_swap,
                expensiveDex.router_v2,
                self.tokenA_address,
            )
            print("Swapping {} to {}...".format(self.tokenA_symbol, self.tokenB_symbol))
            expensiveDex.swap(
                self.tokenA_address,
                self.tokenB_address,
                expensive_quote,
                amount_to_swap,
                reverse_feed=False,
            )
            print(
                ">>>>>III. After {} swapped with {}".format(
                    self.tokenA_symbol, self.tokenB_symbol
                )
            )
            self.get_current_balances()