from brownie import accounts, network, config, interface
from web3 import Web3

NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["hardhat", "development", "ganache"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS + [
    "mainnet-fork",
    "binance-fork",
    "matic-fork",
]

price_feed_mapping = {
    "mainnet-fork": {
        (
            config["networks"][network.show_active()]["dai"],
            config["networks"][network.show_active()]["weth"],
        ): "0x773616E4D11A78F511299002DA57A0A94577F1F4"
    },
    "kovan": {
        (
            config["networks"][network.show_active()]["dai"],
            config["networks"][network.show_active()]["weth"],
        ): "0x22B58f1EbEDfCA50feF632bD73368b2FdA96D541"
    },
}


def get_account(index=None, id=None):
    # accounts[0]
    # accounts.add("env")
    # accounts.load("id")
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]

    else:
        return accounts.add(config["wallets"]["from_key"])


def approve_erc20(
    amount,
    to,
    erc20_address,
    account,
    spender=config["networks"][network.show_active()]["uniswap_router_v2"],
):
    tx_hash = None
    print("Approving ERC20...")
    erc20 = interface.IERC20(erc20_address)
    allowance = erc20.allowance(account, spender)
    if allowance > amount:
        print("You have already allowance {} ERC20 tokens!".format(allowance))
    else:
        tx_hash = erc20.approve(to, amount, {"from": account})
        print("Approved!")
        tx_hash.wait(1)
    return tx_hash


def get_asset_price(
    address_price_feed=None,
):
    # For mainnet we can just do:
    # return Contract(f"{pair}.data.eth").latestAnswer() / 1e8
    address_price_feed = (
        address_price_feed
        if address_price_feed
        else config["networks"][network.show_active()]["dai_eth_price_feed"]
    )
    dai_eth_price_feed = interface.AggregatorV3Interface(address_price_feed)
    latest_price = Web3.fromWei(dai_eth_price_feed.latestRoundData()[1], "ether")
    print(f"The DAI/ETH price is {latest_price}")
    return float(latest_price)