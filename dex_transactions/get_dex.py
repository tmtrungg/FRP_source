
# Get tokens liquidity

import asyncio
from loguru import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import datetime
import time
import tasks
import tasks.eth
import pandas as pd
import aiohttp
from handlers.goplus_handlers import get_goplus_api
from handlers.transpose_handlers import get_transpose_api 
import requests
import json
import time

#Get all DEXs transactions

async def getdex():
    async with aiohttp.ClientSession() as session:
        csv_eth_all = '../../Data/eth_all.csv'
        df_all = pd.read_csv(csv_eth_all)
        df_all = df_all.sort_values(by='id')
        first_id = df_all['id'].iloc[0]
        last_id = df_all['id'].iloc[-1]
        while first_id < last_id:
            df = df[(df_all['id'] >= first_id) & (df_all['id'] <= first_id + 10)]
            error_results = []
            empty_token = []

            for index, row in df.iterrows():
                transaction_hash = row['transaction_hash']
                print(f"Transaction hash: {transaction_hash}")
                all_results = []
                truncated = True

                #Call first time
                try:
                    result = await get_transpose_api(session, "/eth-getdex",{'transaction_hash': transaction_hash})
                    if result['results']['value'] == True:
                        all_results.extend(result['results'])
                except:
                    logger.error(f'Error at {transaction_hash}')
                    error_results.append(transaction_hash)
                    pass
            
            # Update to db 
            try:
                _ = requests.post("http://127.0.0.1:8000/v1/eth-dex/bulk", headers={
                    "accept": "application/json",
                    "Content-Type": "application/json"
                },
                                    data=json.dumps(all_results)) 
            except Exception as e:
                logger.error(f"Error at {result['results']} during snipe database update: {e}")
            first_id += 10 if first_id + 10 < last_id else last_id - first_id
        
        logger.info(f'Liquidity: {id}')
        time.sleep(0.5)

        logger.info('Finish updating liquidity in this patch')
        print('Error token:')
        print(error_results)
        print('Empty liq token:')
        print(empty_token)

async def main_getdex():
    await getdex()

if __name__ == "__main__":
    logger.info("Starting scheduler")
    scheduler = AsyncIOScheduler()
    scheduler.add_job(main_getdex)
    scheduler.start()
    asyncio.get_event_loop().run_forever()
