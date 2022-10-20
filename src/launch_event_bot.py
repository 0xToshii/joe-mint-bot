""" Bot which mints based on event listening on websocket
"""

import argparse
import json
import time
import threading
import websockets
import asyncio
import ssl
import certifi
import concurrent.futures

from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account.account import Account


class event_bot:
    """ stores relevant env variables
    """

    def __init__(self,bot_config,rpcs,nft_address,nft_abi):
        """ Initialize event-listening bot
        args:
            bot_config (dict): includes address, private_key, websocket
            rpcs (list): list of all rpcs for this network
            nft_address (str): address of the NFT contract
            nft_abi (list): abi for the NFT contract
        """
        self.private_key = bot_config['private_key']
        self.account = Account.from_key(self.private_key)
        self.websocket = bot_config['websocket']
        
        self.rpc_connections=[]
        for rpc in rpcs:
            w3 = Web3(Web3.HTTPProvider(rpc))
            w3.middleware_onion.inject(geth_poa_middleware,layer=0)
            self.rpc_connections.append(w3)

        for _ in range(2): # sanity check
            print("rpc connections:",[w3.isConnected() for w3 in self.rpc_connections])
            time.sleep(1)

        self.contract_address = Web3.toChecksumAddress(nft_address)
        self.contract_abi = nft_abi
        self.mint_contract = self.rpc_connections[0].eth.contract(address=self.contract_address, abi=self.contract_abi)

        self.event_topic_hash = self.rpc_connections[0].keccak(text="Initialized(uint256,uint256,uint256,uint256)").hex() # this is the event we are listening for

        # fixed for this event
        self.gas_limit = 300_000
        self.max_gas_in_gwei = 50
        self.gas_tip_in_gwei = 2

        self.base_tx = {
                'type':0x2,
                'chainId':self.rpc_connections[0].eth.chain_id,
                'gas':self.gas_limit,
                'maxFeePerGas':Web3.toWei(self.max_gas_in_gwei,'gwei'),
                'maxPriorityFeePerGas': Web3.toWei(self.gas_tip_in_gwei,'gwei'),
                'nonce':self.rpc_connections[0].eth.get_transaction_count(self.account.address),
                'value':0
        }

        self.contract_function = self.mint_contract.functions.allowlistMint(1)
        contract_tx = self.contract_function.buildTransaction(self.base_tx)
        self.first_signed_tx = self.rpc_connections[0].eth.account.sign_transaction(contract_tx, self.account.privateKey)

        self.pool = concurrent.futures.ThreadPoolExecutor()
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())


    def run_thread_pool(self,signed_tx):
        """ runs transaction execution using threadpool and returns tx status
        """
        tx_futures = []
        for w3 in self.rpc_connections:
            tx_pending = self.pool.submit(w3.eth.send_raw_transaction,signed_tx.rawTransaction)
            tx_futures.append(tx_pending)

        done,timed_out = concurrent.futures.wait(tx_futures,timeout=10) # pause execution

        print("-futures:",len(tx_futures))

        try: # minimal error handling
            tx_hash = tx_futures[0].result().hex()
        except:
            tx_hash = tx_futures[1].result().hex()
        tx_status = self.rpc_connections[0].eth.waitForTransactionReceipt(tx_hash)['status']
        return tx_status


async def start_and_run_listener():
    """ starts event listener for contract 'Initialize' event & handles tx logic
    """
    async with websockets.connect(bot.websocket,ssl=bot.ssl_context) as ws:
        await ws.send(json.dumps({"method":"eth_subscribe",
                                  "id":1, # subscription id can be set to anything
                                  "jsonrpc":"2.0",
                                  "params":["logs",{
                                                      "fromBlock":"latest",
                                                      "address":bot.contract_address,
                                                      "topics":[bot.event_topic_hash]
                                                   }
                                            ]
                                 }))
        resp = await ws.recv()
        print("conn:",resp)
        
        while True:
            try: # listen for event
                message = await asyncio.wait_for(ws.recv(), timeout=10) # waiting for event trigger
                topics_data = json.loads(message)['params']['result']['data']
                topics = [int(topics_data[i:i+64],base=16) for i in range(2,len(topics_data),64)] # abi.decode(uint,uint,uint,unt)
                allow_list_start_time = topics[0]
                # allow_list_price = topics[2] # free mint so irrelevant
                # bot.base_tx['value']=allow_list_price

                print("-got_message:",time.time())
                
                # block execution until 2s before mint
                # simplest way to propagate + ensure no extra tx execution given nonce will be fixed
                while allow_list_start_time-2.0>time.time():
                    time.sleep(0.01)
                
                print("-start_mint:",time.time())
            
                tx_status = bot.run_thread_pool(bot.first_signed_tx) # first tx can be cached

                print("status:",tx_status)

                # backup code to inf loop sending tx if failed previously
                ## if this is reached it indicates bot will lose the race tho
                while tx_status == 0:
                    bot.base_tx['nonce']+=1 # nonce requires updating
                    contract_tx = bot.contract_function.buildTransaction(bot.base_tx)
                    signed_tx = bot.rpc_connections[0].eth.account.sign_transaction(contract_tx, bot.account.privateKey)

                    tx_status = bot.run_thread_pool(signed_tx)

                    print("status:",tx_status)

                bot.base_tx['nonce']+=1 # for testing, unnecessary
                
            except Exception as e: # error handler
                print("-",e)
                continue


if __name__=="__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--config") # gather the config file for this bot
    parser.add_argument("--bot")
    parser.add_argument("--nft_address")
    parser.add_argument("--nft_abi_path")
    parser.add_argument("--websocket") # multiple websocket listeners per bot
    args = parser.parse_args()

    config = json.load(open(args.config))
    bot_config = config[args.bot]
    rpcs = config['rpcs']
    nft_address = args.nft_address
    nft_abi = json.load(open(args.nft_abi_path))['abi'] # @@

    bot_config['websocket']=args.websocket

    print("bot init ...")
    bot = event_bot(bot_config,rpcs,nft_address,nft_abi)


    asyncio.run(start_and_run_listener())

