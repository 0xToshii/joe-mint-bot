""" Used to determine the websocket with the lowest latency
"""

import argparse
import time
import websockets
import asyncio
import ssl
import certifi
import json


async def run_listener():
    """ starts event listener for contract 'Initialize' & handles logging latency
    """
    async with websockets.connect(data['websocket'],ssl=data['ssl_context']) as ws:
        await ws.send(json.dumps({"method":"eth_subscribe",
                                  "id":1, # subscription id can be set to anything
                                  "jsonrpc":"2.0",
                                  "params":["logs",{
                                                      "fromBlock":"latest",
                                                      "address":data['contract_address'],
                                                      "topics":[data['event_topic_hash']]
                                                   }
                                            ]
                                 }))
        resp = await ws.recv()
        print("conn:",resp)
        
        while True:
            try: # listen for event
                message = await asyncio.wait_for(ws.recv(), timeout=10) # waiting for event trigger
                topics_data = json.loads(message)['params']['result']['data']
                received_time = time.time()
                print(received_time)
                
            except Exception as e: # error handler
                #print("-",e)
                continue



if __name__=="__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--contract_address")
    parser.add_argument("--ws_name")
    args = parser.parse_args()

    data = {}
    data['websocket']=args.ws_name
    data['ssl_context']=ssl.create_default_context(cafile=certifi.where())
    data['contract_address']=args.contract_address
    data['event_topic_hash']="0x21adc90360bc280b314eb6502b95564cc7180b3d7cdb300b03a8a2f41de14f3e" # fixed


    asyncio.run(run_listener())

