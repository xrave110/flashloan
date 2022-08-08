from brownie import interface, web3, chain
from sympy import li


class Routerv2Api:
    def __init__(self, account, router_v2):
        self.account = account
        self.router_v2 = router_v2

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

    def get_asset_price(self, address_price_feed, reverted=False):
        price_feed = interface.AggregatorV3Interface(address_price_feed)
        latest_price = web3.fromWei(price_feed.latestRoundData()[1], "ether")
        print(f"Price feed latest data: {latest_price}")
        return float(latest_price)

    def swap(
        self,
        address_from_token,
        address_to_token,
        from_to_price,
        amount,
        reverse_feed=False,
    ):
        path = [
            address_from_token,
            address_to_token,
        ]
        if reverse_feed:
            from_to_price = 1 / from_to_price
        # amountOutMin = int((from_to_price * 0.5) * 10 ** 18)
        # 98 is 2% slippage
        # I get a little weird with units here
        # from_to_price isn't in wei, but amount is
        amountOutMin = int((from_to_price * 0.90) * amount)
        print(
            "Amount: {} amountOutMin: {}".format(
                web3.fromWei(amount, "ether"), web3.fromWei(amountOutMin, "ether")
            )
        )
        timestamp = chain[web3.eth.get_block_number()]["timestamp"] + 120
        print(
            f"->>>> ALLOWANCE: {interface.IERC20(address_from_token).allowance(self.account, self.router_v2.address)}"
        )
        print(
            f"->>>> BALANCEOF: {interface.IERC20(address_from_token).balanceOf(self.account)}"
        )
        swap_tx = self.router_v2.swapExactTokensForTokens(
            amount, 0, path, self.account, timestamp, {"from": self.account}
        )
        swap_tx.wait(1)
        return swap_tx

    def get_pair_contract(self, address_token_a, address_token_b):
        factory_address = self.router_v2.factory()
        print(factory_address)
        factory = interface.IFactory(factory_address)
        pair_address = factory.getPair(address_token_a, address_token_b)
        print(pair_address)
        pair = interface.IUniswapV2Pair(pair_address)
        return pair

    def get_pair_liquidity(self, address_token_a, address_token_b):
        pair = self.get_pair_contract(address_token_a, address_token_b)
        [reserves_a, reserves_b, a] = pair.getReserves()
        pair_account_balance = pair.balanceOf(self.account)
        pair_total_balance = pair.totalSupply()
        factor = pair_account_balance / pair_total_balance
        # print(
        #     "Your liquidity is {}\nPair liquidity is {}\nYour Tokens: {} DAI and {} ETH\nToken Reserves: {} DAI and {} ETH\n".format(
        #         web3.fromWei(pair_account_balance, "ether"),
        #         web3.fromWei(pair_total_balance, "ether"),
        #         float(web3.fromWei(reserves_a, "ether")) * factor,
        #         float(web3.fromWei(reserves_b, "ether")) * factor,
        #         web3.fromWei(reserves_a, "ether"),
        #         web3.fromWei(reserves_b, "ether"),
        #     )
        # )
        return pair.balanceOf(self.account)

    def remove_liquidity(self, address_token_a, address_token_b):
        liquidityTokens = self.get_pair_liquidity(address_token_a, address_token_b)
        timestamp = chain[web3.eth.get_block_number()]["timestamp"] + 120
        pair = self.get_pair_contract(address_token_a, address_token_b)
        self.approve_erc20(liquidityTokens, self.router_v2.address, pair.address)
        self.router_v2.removeLiquidity(
            address_token_a,
            address_token_b,
            liquidityTokens,
            0,
            0,
            self.account,
            timestamp,
            {"from": self.account},
        )
        liquidityTokens = self.get_pair_liquidity(address_token_a, address_token_b)
        return liquidityTokens

    def addLiquidity(
        self,
        address_token_a,
        address_token_b,
        amount_a_desired,
        from_to_price,
    ):
        """
        amount_a_desired, amount_b_desired - possible 0 for kovan and real value for mainnet-fork
        """
        print("1 TokenA is {} TokenB".format(1 / from_to_price))
        amount_b_desired = from_to_price * amount_a_desired
        print(
            "So I will pool {} TokenB and {} TokenA".format(
                web3.fromWei(amount_a_desired, "ether"),
                web3.fromWei(amount_b_desired, "ether"),
            )
        )

        amount_a_min = 0.9 * amount_a_desired
        amount_b_min = 0.9 * amount_b_desired

        tx = self.approve_erc20(
            amount_a_desired, self.router_v2.address, address_token_a
        )
        print("Approved {} of token a".format(amount_a_desired))
        tx = self.approve_erc20(
            amount_b_desired, self.router_v2.address, address_token_b
        )
        print("Approved {} of token b".format(amount_b_desired))
        timestamp = chain[web3.eth.get_block_number()]["timestamp"] + 120
        print(
            " address_token_a: {}\n address_token_b: {}\n amount_a_desired: {}\n amount_b_desired: {}\n amount_a_min: {}\n amount_b_min: {}\n account: {}\n timestamp: {}".format(
                address_token_a,
                address_token_b,
                amount_a_desired,
                amount_b_desired,
                amount_a_min,
                amount_b_min,
                self.account,
                timestamp,
            )
        )
        pair = self.get_pair_contract(address_token_a, address_token_b)
        [tokenA_reserves, tokenB_reserves, timestampReceived] = pair.getReserves()
        print(
            f"Reserves before providing liquidity {web3.fromWei(tokenA_reserves, 'ether')} tokenA and {web3.fromWei(tokenB_reserves, 'ether')} tokenB"
        )
        liquidity_tx = self.router_v2.addLiquidity(
            address_token_a,
            address_token_b,
            amount_a_desired,
            amount_b_desired,
            amount_a_min,
            amount_b_min,
            self.account,
            timestamp,
            {"from": self.account},
        )
        liquidity_tx.wait(1)
        [tokenA_reserves, tokenB_reserves, timestampReceived] = pair.getReserves()
        print(
            f"Reserves after providing liquidity {web3.fromWei(tokenA_reserves, 'ether')} tokenA and {web3.fromWei(tokenB_reserves, 'ether')} tokenB"
        )
        print(f"You received {liquidity_tx} DAI/ETH liquidity tokens")
        return liquidity_tx
