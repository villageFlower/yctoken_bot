import asyncio
import json
from web3 import Web3
from websockets import connect

# Note there are some issues with older websocket libraries soooo do the following:
# pip install --upgrade web3
# pip install --upgrade websockets
# --------------------------Connection Setup stuff -------------------------------#
INFURA_WS = 'wss://mainnet.infura.io/ws/v3/9110a9490de6477184406113ce4854a4'
INFURA_HTTP = 'https://mainnet.infura.io/v3/9110a9490de6477184406113ce4854a4'
web3 = Web3(Web3.HTTPProvider(INFURA_HTTP))
print(f'Connected via HTTP: {web3.is_connected()}')


# --------------------------Connection Setup stuff -------------------------------#


def EventHandler(pending_tx):
    """Takes in a subscription transacton response as pending_tx
       Then currently prints out data or can be modified for whatever"""
    transaction = json.loads(pending_tx)
    txHash = transaction['params']['result']
    transaction = web3.eth.get_transaction(txHash)
    # Filter transactions to Uniswap Router:
    if transaction['to'] == web3.to_checksum_address('0xEf1c6E67703c7BD7107eed8303Fbe6EC2554BF6B'):
        print(web3.to_hex(transaction['hash']), transaction)
        # Get the input data
        input_data = transaction.input

        # Define the function signatures
        swap_functions = ['0x3593564c']

        # Check if the input data contains a swap function
        if input_data[:10] in swap_functions:
            # Extract the token address from the input data
            token_address = '0x' + input_data[74:114]

            # Fetch the token symbol and decimals from the token contract
            # token_contract = web3.eth.contract(address=token_address, abi=YOUR_TOKEN_ABI)
            # token_symbol = token_contract.functions.symbol().call()
            # token_decimals = token_contract.functions.decimals().call()

            # Print the token details
            print('Token Address:', token_address)
            # print('Token Symbol:', token_symbol)
            # print('Token Decimals:', token_decimals)
        else:
            print('This transaction is not a Uniswap swap transaction.')


# --------------------------Start Subscribe Pending TX -------------------------------#
# This code actually grabs the pending transactons from the mempool
# Reference: https://docs.alchemy.com/reference/newpendingtransactions
#           https://websockets.readthedocs.io/en/3.4/intro.html
async def subscribePendingTX():
    """Subscribes to the mempool listening for pending transactions
       Sends off the responses to be processed by the eventhandler function"""
    async with connect(INFURA_WS) as ws:
        await ws.send('{"jsonrpc": "2.0", "id": 1, "method": "eth_subscribe", "params": ["newPendingTransactions"]}')

        while True:
            try:
                pending_tx = await asyncio.wait_for(ws.recv(), timeout=15)
                EventHandler(pending_tx)

            except KeyboardInterrupt:
                exit()
            except:
                pass


# --------------------------End Subscribe Pending TX -------------------------------#

if __name__ == "__main__":
    asyncio.run(subscribePendingTX())
