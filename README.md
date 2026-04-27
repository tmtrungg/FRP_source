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

- **Ethereum node:** Geth (Go Ethereum), run as an **archive** node
  (the measurement reaches back to 2018 and requires historical state).
- **Python:** 3.8+ with `web3.py`, `pandas`, `numpy`, `matplotlib`,
  `jupyter`, `tqdm`.
- **System:** ~1 TB disk (SSD recommended), stable internet for syncing.

```bash
pip install -r requirements.txt
```

---

## Stage 1 — Raw Ethereum data collection

The collection scaffolding is forked and extended from
[this guide](https://medium.com/@victor.denisov/how-to-retrieve-data-from-the-ethereum-blockchain-386b03bea4a)
([source repo](https://github.com/grgcmz/eth-data-analysis)).

**Step 1.** Install and sync Geth as an archive node:

```bash
geth --syncmode "full" --gcmode "archive" \
     --http --http.api "eth,net,web3"
```

**Step 2.** Pull all transactions in the target block range using `web3.py`.
Because of memory and storage constraints, we iterate in small batches
(default 5 blocks at a time):

```python
from web3 import Web3
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

for block in range(6_627_000, 21_379_911):
    block_data = w3.eth.get_block(block, full_transactions=True)
    # ... persist batch to disk
```

**Step 3.** Anonymize public addresses with
[`dex_transactions/data_anon.py`](./dex_transactions/data_anon.py). On-chain
data is public, but we mask the middle bytes of each wallet/token address
to avoid amplifying scammer attribution beyond what the analysis requires
(see *Ethical Considerations* in the paper).

**Step 4.** Persist the anonymized dataset to local storage for downstream
stages.

---

## Stage 2 — DEX transaction filtering

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

## Stage 3 — FRP labeling

The labeling step applies the formal FRP definition (Definition 2, §4.3)
to the collected pool set.

**Pool filtering.** We retain only LPs whose observable lifetime
(first to last on-chain activity) is at most 100 days, as motivated in §7.4.
This reduces 384,029 LPs to **303,614** short-lived LPs.

**Predicate evaluation.** For each remaining pool, we evaluate the three
atomic predicates from §4.1:

- **(A) `RetainLP`** — the deployer's initial LP tokens are not burned or
  time-locked.
- **(B) `Impact`** — every inflated sell satisfies `v_i / V_i ≤ θ`, with
  `θ = 0.9` (matching prior work).
- **(C) `SellerIsOwner`** — either no owner-originated sell exists, or
  every owner-originated sell stays sub-threshold.

A pool is labeled FRP iff (A) holds and (B), (C) jointly hold across the
inflated-selling trace. Applying this rule to the 303,614 short-lived LPs
yields the **105,434 FRP-labeled pools** released in
[`analysis/labeled_pool_anonimized.json`](./analysis/labeled_pool_anonimized.json).

**Validation.** Two checks accompany the labeled set:

- A random sample of 200 flagged pools was manually verified to satisfy
  all three predicates (results in `analysis/manual_inspection_200.csv`).
- The canonical rug-pull heuristics from prior work [3, 5] were
  re-implemented and applied to the 105,434 FRP pools; none were detected
  by the canonical rules, confirming that FRP cases are structurally
  distinct from classical rug pulls and not double-counted.

---

## Stage 4 — Measurement and analysis

The measurement code is in [`analysis/`](./analysis), implemented as a mix
of Python scripts (`python3 filename.py`) and Jupyter notebooks (run
cell-by-cell). It corresponds directly to Algorithm 1 in Appendix D and
covers three perspectives:

- **Actor-centric analysis (§6.1)** — wallet-count distribution, owner
  involvement over time, and recurrent inflated-seller wallets. Reproduces
  Figure 3.
- **Action-centric analysis (§6.2)** — first-sell delay, sell span, and
  inflated-sell counts, stratified by single/multi-wallet and
  owner/non-owner cohorts. Reproduces Table 2.
- **Behavior categorization (§6.3)** — binning pools by wallet count and
  total sell count, identifying the three dominant clusters
  (Minimal Drains, Moderate Networks, Distributed Campaigns). Reproduces
  Figures 4–5 and Table 3.

All notebooks read `analysis/labeled_pool_anonimized.json` and write
figures to `analysis/figures/`.

---

## Released vs. not released

We release the labeled FRP dataset, all per-pool transaction traces for the
105,434 flagged pools (34.19 M transactions), the predicate and labeling
code, the baseline cross-check, and the analysis notebooks.

The full raw corpus underlying Stage 1 — approximately **1.1 billion**
Ethereum transactions — exceeds the size limits of anonymous hosting and
is not bundled here. It can be reconstructed deterministically from any
Ethereum archive node using the block range and DEX contract addresses
listed above.

---

## License

Released under the MIT License (see `LICENSE`). Datasets are derived from
public Ethereum on-chain data and are similarly unrestricted.
