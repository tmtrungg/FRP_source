# How To Detect The Fragmented Rug Pull?
## OVERVIEW

This repository implements the code and data analytics pipeline described in the paper *"How To Detect The Fragmented Rug Pull?"*. The primary goal is to identify and analyze the **FRP** scam, a newly defined type of fraudulent activity in decentralized finance (DeFi). We use data from Ethereum blocks **6,627,000 (November 2, 2018)** to **21,379,910 (March 5, 2025)**, covering the lifespan of DeFi liquidity pools. Our study analyzes data of FRP LPs extracted from the six largest decentralized exchanges (DEXs) on Ethereum.

## RAW ETHEREUM DATA COLLECTION

### Resource

For the step of raw data collection from Ethereum, we have forked and extended the code from [this guide](https://medium.com/@victor.denisov/how-to-retrieve-data-from-the-ethereum-blockchain-386b03bea4a) (github source: [ETH Data Analysis source code](https://github.com/grgcmz/eth-data-analysis)) as the base for our implementation. These resources helped us establish the pipeline for data extraction of Ethereum network.


### Requirements
- **Ethereum Node:** Geth (Go Ethereum)
- **Python Environment:** Python 3.8+ with `web3.py`, `pandas`, `matplotlib`, `numpy`.
- **System Resources:** 1TB+ disk space, SSD, stable internet.

### Step by step break down

#### Step 1: Set Up Geth Node

Install and configure Geth (Go Ethereum) from the forked code to interact with the Ethereum blockchain. Sync the node to enable querying historical blocks.

```bash
geth --syncmode "fast" --http --http.api "eth,net,web3"
```

#### Step 2: Use web3.py to extract transaction data:

```bash
from web3 import Web3
web3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
for block in range(6627000, 21379910):
    block_data = web3.eth.getBlock(block, full_transactions=True)
```
Due to memory and storage constraints, we process the blocks in this step in smaller ranges (e.g., 5 blocks at a time from 6627000 to 21379910) to ensure efficient data handling.

#### Step 3: Anonymizing public data ([`data anonimyze`](./dex_transactions/data_anon.py)).

#### Step 4: Store the data in the database.

## TRANSACTION DATA COLLECTION AMONG DEXes

To identify and analyze transactions specific to DEX activity, we use the **Chainalysis API** ([documentation and usage guide](https://docs.transpose.io/)). This API allows us to filter transactions to include only those related to activities on the six largest DEXs mentioned in the paper: **Uniswap, SushiSwap, Balancer, Curve, PancakeSwap, and BancorSwap**.

From the raw dataset, we query each of the transaction hash to the database of **Chainalysis API** for getting result of "Whether this transaction is a DEX-related transaction or not?" by using [`dex_transactions/get_dex.py`](./dex_transactions/get_dex.py) calling the SQL endpoint of [`dex_transactions/getdex_sql.tex`](./dex_transactions/getdex_sql.tex), which will return a "yes or no" result for each query. We update all transaction data into separate dataset. Afterward, the dataset of all liquidity pool that involved in the DEXes transactions is gathered using the SQL endpoint of [`dex_transactions/getpool_sql.tex`](./dex_transactions/getpool_sql.tex)

## ANALYSIS

From the FRP data that got from applying the definition to raw data, the code for analysis is mainly written in .py and .ipynb files, which can be run with the previously generated datasets (using ```python3 filename.py``` for .py files or cell execution for different steps for .ipynb files). The folder [`analysis`](./analysis) includes the source code for:

- Actor-Centric Analysis
- Action-Centric Analysis
- Behavior Categorization

