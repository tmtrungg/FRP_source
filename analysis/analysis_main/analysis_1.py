import requests
import aiohttp
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pandas as pd
import time
import numpy as np
from loguru import logger
import warnings
warnings.filterwarnings("ignore")
import json
import asyncio

async def data_gen():
    async with aiohttp.ClientSession() as session:
        logger.info("Starting getting csv")

        csv_basic = '../../Data/important/basic_eth_100d_scam.csv'
        csv_scam = '../../Data/important/info_eth_100dscam.csv'
        csv_scamliq = '../../Data/important/liq_eth_100d_scam.csv'
        CSV_UNIQUEWALLET = '../../Data/important/analysis/unique_wallets.csv'
        CSV_IASELLER     = '../../Data/important/analysis/rugpull_sellers.csv'

        df_scaminfo = pd.read_csv(csv_scam)
        df_scamliq = pd.read_csv(csv_scamliq)

        logger.info("Done getting csv")

        CHECKPOINT_EVERY = 100
        unique_wallet_records = []
        ia_seller_records = []

        unique_wallet_batch = []
        ia_seller_batch = []

        for outer_index, outer_row in df_scaminfo.iterrows():
            try:
                pool_address = outer_row['pool_address']
                owner = outer_row['token_owner']
                base_token = outer_row['token_paired_address']
                paired_token = outer_row['token_address']

                df_oneliq = df_scamliq[df_scamliq['pool_address'] == pool_address]
                df_oneliq.loc[:, 'timestamp'] = pd.to_datetime(df_oneliq['timestamp'])
                df_oneliq = df_oneliq.sort_values(by='timestamp')

                unique_wallet_count = df_oneliq['sender_address'].nunique()
                unique_wallet_batch.append({
                    'outer_index': outer_index,
                    'pool_address': pool_address,
                    'unique_wallet_count': unique_wallet_count
                })

                df_oneliq = df_oneliq[df_oneliq['token_address'].str.lower() == paired_token.lower()]
                df_oneliq['category'] = df_oneliq['category'].str.lower()
                df_oneliq = df_oneliq[df_oneliq['category'].isin(['buy', 'sell'])]

                seller_candidates = set(
                    df_oneliq.loc[df_oneliq['category'] == 'sell', 'sender_address'].dropna().unique()
                )

                if not seller_candidates:
                    print(f"No seller candidates for pool {pool_address}, {outer_index}")

                df_rel = df_oneliq[df_oneliq['sender_address'].isin(seller_candidates)].copy()

                # scan chronologically per pool
                cum_buys  = {w: 0.0 for w in seller_candidates}
                cum_sells = {w: 0.0 for w in seller_candidates}
                rugpull_sellers = set()

                for _, row in df_rel.iterrows():
                    w   = row['sender_address']
                    act = row['category']
                    amt = float(row['amount_token'])  # amount of the paired token in this trade

                    if act == 'buy':
                        cum_buys[w] += abs(amt)

                    elif act == 'sell':
                        # condition A: this single sell exceeds all prior buys
                        if amt > cum_buys[w]:
                            rugpull_sellers.add(w)

                        # condition B: cumulative sells exceed cumulative buys
                        cum_sells[w] += amt
                        if cum_sells[w] > cum_buys[w]:
                            rugpull_sellers.add(w)

                ia_seller_batch.append({
                    'pool_address': pool_address,
                    'rugpull_sellers': json.dumps(sorted(rugpull_sellers))
                })

                if (outer_index) % CHECKPOINT_EVERY == 0:
                    pd.DataFrame(unique_wallet_batch).to_csv(CSV_UNIQUEWALLET, index=False, mode='a', header=False)
                    pd.DataFrame(ia_seller_batch).to_csv(CSV_IASELLER, index=False, mode='a', header=False)
                    unique_wallet_batch.clear()
                    ia_seller_batch.clear()
                    print(f"Checkpoint saved at {outer_index}")
            except Exception as e:
                logger.error(f"Error processing pool at index {outer_index}, address {pool_address}: {e}")
                continue

        if unique_wallet_batch:
            pd.DataFrame(unique_wallet_batch).to_csv(CSV_UNIQUEWALLET, index=False, mode='a', header=False)
        if ia_seller_batch:
            pd.DataFrame(ia_seller_batch).to_csv(CSV_IASELLER, index=False, mode='a', header=False)

        
        logger.info("Done for all data")


if __name__ == "__main__":
    logger.info("Starting scheduler")
    scheduler = AsyncIOScheduler()
    scheduler.add_job(data_gen)
    scheduler.start()
    asyncio.get_event_loop().run_forever()

