from brownie import web3, interface


class Arbitrage:
    def __init__(
        self,
        dex1,
        dex2,
        tokenA_address,
        tokenB_address,
        address_tokens_price_feed,
        address_base_token_price_feed,
    ):
        self.dex1 = dex1
        self.dex2 = dex2
        self.tokenA_address = tokenA_address
        self.tokenB_address = tokenB_address
        self.tokenA_symbol = interface.IERC20(tokenA_address).symbol()
        self.tokenB_symbol = interface.IERC20(tokenB_address).symbol()
        self.address_tokens_price_feed = address_tokens_price_feed
        self.address_base_token_price_feed = address_base_token_price_feed

    def check_pools(self):
        dex1_quote = self.dex1.get_pair_quote(self.tokenA_address, self.tokenB_address)
        print("Quote: {}".format(dex1_quote))
        print(
            "Dex1 :\n1 {} is {} {} ".format(
                self.tokenA_symbol, dex1_quote, self.tokenB_symbol
            )
        )
        dex2_quote = self.dex2.get_pair_quote(self.tokenA_address, self.tokenB_address)
        print("Quote: {}".format(dex2_quote))
        print(
            "Dex2:\n1 {} is {} {} ".format(
                self.tokenA_symbol, dex2_quote, self.tokenB_symbol
            )
        )
        return [dex1_quote, dex2_quote]

    def get_current_balances(self):
        latest_price = self.dex1.get_asset_price(self.address_tokens_price_feed)
        base_token_price = self.dex1.get_asset_price(
            self.address_base_token_price_feed
        ) * (
            10 ** 10
        )  # to consider 8 decimals instead of 18
        tokenA_balance = web3.fromWei(
            interface.IERC20(self.tokenA_address).balanceOf(self.dex1.account),
            "ether",
        )
        tokenB_balance = web3.fromWei(
            interface.IERC20(self.tokenB_address).balanceOf(self.dex1.account),
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
        usd_balance = (base_token_price * float(tokenA_balance)) + (
            float(tokenB_balance) * latest_price * base_token_price
        )
        print(" >>>>>>>>>> Total balance in USD: {} <<<<<<<<<<<< ".format(usd_balance))
        return usd_balance

    def perform_arbitrage(self, amount):
        print(
            ">>>>>I. Before {} swapped to {}".format(
                self.tokenA_symbol, self.tokenB_symbol
            )
        )
        [dex1_quote, dex2_quote] = self.check_pools()

        print("Gas price is {}".format(web3.eth.generate_gas_price()))
        # print("Gas limit is {}".format(web3.eth.estimate_gas()))
        if dex1_quote > dex2_quote:
            print(
                "Dex1 has more expensive {} (cheaper {})".format(
                    self.tokenA_symbol, self.tokenB_symbol
                )
            )
            usd_balance = self.buy_cheap(
                amount, self.dex1, self.dex2, dex2_quote, dex1_quote
            )

        else:
            print(
                "Dex2 has more expensive {} (cheaper {})".format(
                    self.tokenA_symbol, self.tokenB_symbol
                )
            )
            usd_balance = self.buy_cheap(
                amount, self.dex2, self.dex1, dex1_quote, dex2_quote
            )
        return usd_balance

    def estimate_fees(self, amount, cheap_quote):
        protocol_fee = 0.003 * amount * cheap_quote * 2
        estimated_gas_limit = 21000 * 3  # TODO temporary hardcoded
        print("Protocol fee is: {}".format(protocol_fee))
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
                self.tokenA_address,
            )
            print(
                "Allowance for tokenA {} \n amount to swap: {} ".format(
                    float(
                        interface.IERC20(self.tokenA_address).allowance(
                            cheapDex.account, cheapDex.router_v2
                        )
                    ),
                    amount_to_swap,
                )
            )

            print("Swapping {} to {}...".format(self.tokenA_symbol, self.tokenB_symbol))
            cheapDex.swap(
                self.tokenA_address,
                self.tokenB_address,
                cheap_quote,
                amount_to_swap,
                reverse_feed=True,
            )
            print(
                ">>>>>II. After {} swapped to {}".format(
                    self.tokenA_symbol, self.tokenB_symbol
                )
            )
            self.get_current_balances()
            amount_to_swap = float(
                interface.IERC20(self.tokenB_address).balanceOf(expensiveDex.account)
            ) - float(web3.toWei(0.001, "ether"))
            # - float(web3.toWei(float(fees) * 1.3, "ether")
            # )  # (fees * 1.3) temporary assumption
            expensiveDex.approve_erc20(
                amount_to_swap,
                expensiveDex.router_v2,
                self.tokenB_address,
            )
            print("Swapping {} to {}...".format(self.tokenB_symbol, self.tokenA_symbol))
            expensiveDex.swap(
                self.tokenB_address,
                self.tokenA_address,
                expensive_quote,
                amount_to_swap,
                reverse_feed=False,
            )
            print(
                ">>>>>III. After {} swapped to {}".format(
                    self.tokenB_symbol, self.tokenA_symbol
                )
            )
            return self.get_current_balances()