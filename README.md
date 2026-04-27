# How To Detect The Fragmented Rug Pull?

This repository implements the data and analysis pipeline for the paper
*"How To Detect The Fragmented Rug Pull?"*. We identify and analyze the
**Fragmented Rug Pull (FRP)** scam, a newly defined class of fraudulent
activity in DeFi, on Ethereum blocks **6,627,000 (Nov 2, 2018)** to
**21,379,910 (Mar 5, 2025)** across the six largest DEXs (Uniswap,
SushiSwap, Balancer, Curve, PancakeSwap, BancorSwap).

The pipeline follows the four stages described in the paper:
**(1) raw data collection**, **(2) DEX-level filtering**,
**(3) FRP labeling**, and **(4) measurement and analysis**.

---

## Requirements

- **Ethereum node:** Geth (Go Ethereum).
- **Python:** 3.8+ with `web3.py`, `pandas`, `matplotlib`, `numpy`.
- **System:** ~1 TB disk space, SSD recommended, stable internet.

---

## Raw Ethereum data collection

The collection scaffolding is forked and extended from
[this guide](https://medium.com/@victor.denisov/how-to-retrieve-data-from-the-ethereum-blockchain-386b03bea4a)
([source repo](https://github.com/grgcmz/eth-data-analysis)).

**Step 1.** Install and sync Geth to query historical blocks:

```bash
geth --syncmode "fast" --http --http.api "eth,net,web3"
```

**Step 2.** Pull all transactions in the target block range using `web3.py`.
Because of memory and storage constraints, we iterate in small batches
(e.g. 5 blocks at a time):

```python
from web3 import Web3
web3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
for block in range(6627000, 21379910):
    block_data = web3.eth.getBlock(block, full_transactions=True)
```

**Step 3.** Anonymize public addresses with
[`dex_transactions/data_anon.py`](./dex_transactions/data_anon.py). On-chain
data is public, but we mask the middle bytes of each wallet/token address
to avoid amplifying scammer attribution beyond what the analysis requires
(see *Ethical Considerations* in the paper).

**Step 4.** Store the data in the database for downstream stages.

---

## DEX transaction filtering

To restrict the corpus to DEX activity, each transaction hash is queried
against the **Chainalysis / Transpose API**
([documentation](https://docs.transpose.io/)) to determine whether it
interacts with one of the six target DEXs.

This is driven by [`dex_transactions/get_dex.py`](./dex_transactions/get_dex.py),
which calls the SQL endpoint defined in
[`dex_transactions/getdex_sql.tex`](./dex_transactions/getdex_sql.tex) and
returns a yes/no verdict per transaction. Once DEX-related transactions
are isolated, the full set of involved liquidity pools is assembled with
[`dex_transactions/getpool_sql.tex`](./dex_transactions/getpool_sql.tex).

This stage produces **384,029 LPs** across the six DEXs, distributed as in
Table 1 of the paper.

---

## FRP labeling

FRP labeling follows the formal definition in the paper (Definition 2,
§4.3), which rests on the three atomic predicates from §4.1:

- **(A) `RetainLP`** - the deployer's initial LP tokens are not burned or
  time-locked.
- **(B) `Impact`** - every inflated sell satisfies `v_i / V_i ≤ θ`, with
  `θ = 0.9` (matching prior work).
- **(C) `SellerIsOwner`** - either no owner-originated sell exists, or
  every owner-originated sell stays sub-threshold.

These predicates, together with the ≤100-day lifetime filter (§7.4), are
encoded directly in the SQL queries used during Stage 2 - primarily in
[`dex_transactions/getpool_sql.tex`](./dex_transactions/getpool_sql.tex) -
so that pool selection, predicate evaluation, and FRP labeling are
performed in a single pass over the indexed transaction data rather than
as a separate downstream step. The query returns the **105,434
FRP-labeled pools** released in
[`analysis/labeled_pool_anonimized.json`](./analysis/labeled_pool_anonimized.json),
filtered from the **303,614** short-lived pools in the underlying corpus
of **384,029** collected LPs.

---

## Measurement and analysis

The measurement code is in [`analysis/`](./analysis), implemented as a mix
of Python scripts (`python3 filename.py`) and Jupyter notebooks (run
cell-by-cell). It corresponds to Algorithm 1 in Appendix D and covers
three perspectives:

- **Actor-centric analysis (§6.1)** - wallet-count distribution, owner
  involvement over time, and recurrent inflated-seller wallets. Reproduces
  Figure 3.
- **Action-centric analysis (§6.2)** - first-sell delay, sell span, and
  inflated-sell counts, stratified by single/multi-wallet and
  owner/non-owner cohorts. Reproduces Table 2.
- **Behavior categorization (§6.3)** - binning pools by wallet count and
  total sell count, identifying the three dominant clusters
  (Minimal Drains, Moderate Networks, Distributed Campaigns). Reproduces
  Figures 4–5 and Table 3.

Extended motivation case studies referenced in §3 are provided in
[`analysis/motivation_examples.md`](./analysis/motivation_examples.md).

---

## What is and isn't released

We release the labeled FRP dataset, the labeling and analysis code, and
the analysis notebooks. The full raw transaction corpus collected in
Stage 1 - approximately **1.1 billion** Ethereum transactions - exceeds
the practical size limits of anonymous hosting and is not bundled here.
It can be reconstructed from any Ethereum archive node using the block
range and DEX list above.
