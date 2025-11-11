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
        all_results = []

        for index, row in df.iterrows():
            pool_address = row['pool_address']
            print(pool_address)

            #Call first time
            try:
                result = await get_transpose_api(session, "/getpool_fromadd2",{'pool': pool_address})
                if result['results']:
                    for i in result['results']:
                        all_results.append(i)
                else:
                    print('no pair')
                
            except:
                logger.error(f'Error at this token {pool_address}')
                pass

        logger.info('Finish updating liquidity in this patch')
        all_results_df = pd.DataFrame(all_results)
        print('df',all_results_df)
        all_results_df.to_csv('../Data/important/info_eth_legit30.csv', index=False)

async def tokengetliq():
    await getliq()

if __name__ == "__main__":
    logger.info("Starting scheduler")
    scheduler = AsyncIOScheduler()
    scheduler.add_job(tokengetliq)
    scheduler.start()
    asyncio.get_event_loop().run_forever()
