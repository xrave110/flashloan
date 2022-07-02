from brownie import interface


class Routerv2Api:
    def __init__(self, amount_to_swap, account, router_v2):
        self.amount_to_swap = amount_to_swap
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