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

async def data_anon():
    async with aiohttp.ClientSession() as session:
        df = pd.read_csv('../../Data/eth_alltokens.csv')
        df_id_token = pd.read_csv('../../Data/address_id_token.csv')
        df_id_pool = pd.read_csv('../../Data/address_id_pool.csv')
        df_id_sender = pd.read_csv('../../Data/address_id_sender.csv')
        print(df.head())

        for index, row in df.iterrows():
            address = row['unverified_token']
            pool_address = row['pool_address']
            sender = row['sender_address']

            if address in df_id_token['address'].values:
                address_id = df_id_token.loc[df_id_token['address'] == address, 'id'].values[0]
            else:
                address_id = generate_unique_id(df_id_token['id'].values)

            if pool_address in df_id_pool['address'].values:
                pool_address_id = df_id_pool.loc[df_id_pool['address'] == pool_address, 'id'].values[0]
            else:
                pool_address_id = generate_unique_id(df_id_pool['id'].values)

            if sender in df_id_sender['address'].values:
                sender_id = df_id_sender.loc[df_id_sender['address'] == sender, 'id'].values[0]
            else:
                sender_id = generate_unique_id(df_id_sender['id'].values)
            
            formatted_address = address[:5] + "..." + address[-5:]
            formatted_pool_address = pool_address[:5] + "..." + pool_address[-5:]
            formatted_sender = sender[:5] + "..." + sender[-5:]

            df.at[index, 'unverified_token'] = formatted_address
            df.at[index, 'pool_address'] = formatted_pool_address
            df.at[index, 'sender_address'] = formatted_sender

            df.at[index, 'address_id'] = address_id
            df.at[index, 'pool_address_id'] = pool_address_id
            df.at[index, 'sender_id'] = sender_id
            df.to_csv('../../Data/eth_alltokens.csv', index=False)


async def data_anonimous():
    await data_anon()

if __name__ == "__main__":
    logger.info("Starting scheduler")
    scheduler = AsyncIOScheduler()
    scheduler.add_job(data_anonimous)
    scheduler.start()
    asyncio.get_event_loop().run_forever()
