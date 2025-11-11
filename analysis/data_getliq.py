# Get tokens liquidity

import asyncio
from loguru import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import datetime
import time
import pandas as pd
import aiohttp
from handlers.goplus_handlers import get_goplus_api
from handlers.transpose_handlers import get_transpose_api 
import requests
import json
import time

#Get info of excel file's token liquidity

async def getliq():
    async with aiohttp.ClientSession() as session:
        #402316, from start to end-1
        csv_eth_all = '../Data/important/basic_eth_legit30.csv'
        df = pd.read_csv(csv_eth_all)

        #len = 201505
        tempt_df = df.iloc[0:50000]

        error_results = []
        empty_token = []

        for index, row in df.iterrows():
            pool_address = row['pool_address']
            print(pool_address)
            all_results = []
            truncated = True

            #Call first time
            try:
                result = await get_transpose_api(session, "/eth-getliq2",{'pool_address': pool_address})
                all_results.extend(result['results'])
                truncated = result['stats']['truncated']
                try:
                    last_block = result['results'][-1]['block_number']
                except Exception as e:
                    logger.error(f'Empty liq at this token {pool_address}')
                    empty_token.append(pool_address)
                    pass
                # While loop if truncated
                try:
                    while truncated:
                        try:
                            result = await get_transpose_api(session, "/eth-getliq-extend2",{'pool_address': pool_address, 'block_number': last_block})
                            all_results.extend(result['results'])
                            truncated = result['stats']['truncated']
                            last_block = result['results'][-1]['block_number']
                        except Exception as e: 
                            logger.error('No liquidity')
                            pass
                except Exception as e: 
                    pass
            except:
                logger.error(f'Error at this token {pool_address}')
                error_results.append(pool_address)
                pass

            try:
                _ = requests.post("http://127.0.0.1:8000/v1/eth-alltokens-liquidity/bulk", headers={
                    "accept": "application/json",
                    "Content-Type": "application/json"
                },
                                    data=json.dumps(all_results)) 
            except Exception as e:
                logger.error(f"Error at {result['results']} during snipe database update: {e}")
            
            logger.info(f'Liquidity: {index}')
            print(f'Done updating liquidity of pool no {index}, pool address {pool_address}')

        logger.info('Finish updating liquidity in this patch')
        print('Error token:')
        print(error_results)
        print('Empty liq token:') 
        print(empty_token)

async def tokengetliq():
    await getliq()

if __name__ == "__main__":
    logger.info("Starting scheduler")
    scheduler = AsyncIOScheduler()
    scheduler.add_job(tokengetliq)
    scheduler.start()
    asyncio.get_event_loop().run_forever()
