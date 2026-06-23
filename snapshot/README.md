# ROBARK whitelist snapshot

Builds the ROBARK allowlist from **OpenSea's top collections**. A wallet is
eligible if it holds an NFT from any collection in the eligible set — sourced as
OpenSea's **top 20 trending** + **top 20 featured** collections.

The site never labels them "trending/featured" — they're shown together as the
**eligible collections** roster on the checker page.

## Setup

```bash
cd snapshot
cp .env.example .env        # add ALCHEMY_API_KEY and OPENSEA_API_KEY
npm install
```

- **Alchemy key** — collection images + holder enumeration. https://dashboard.alchemy.com
- **OpenSea key** — the top trending/featured rankings. https://docs.opensea.io/reference/api-keys

## Usage

```bash
# 1) Refresh the eligible-collection list + PFP images.
#    Writes web/data/whitelist-collections.json (consumed by the website).
npm run snapshot

# 2) Take the FINAL holder snapshot the website checks against.
#    Writes web/data/snapshot.json (per-wallet eligible collections) +
#    output/snapshot-wallets.csv + output/snapshot-breakdown.json.
python make_snapshot.py            # needs ALCHEMY_API_KEY in env

# 3) (optional) Per-wallet mint allowlist incl. supporters, for the contract.
#    Writes output/allowlist.json (+ output/allowlist-wallets.txt).
node snapshot.js --holders
```

> The checker reads `web/data/snapshot.json` directly (no live Alchemy call) —
> the snapshot is final. Re-run `make_snapshot.py` only if you re-take it.

### What each output is for

| File | Purpose |
| --- | --- |
| `web/data/whitelist-collections.json` | The eligible set the **website** reads. The checker matches a pasted wallet's collections against this list live (via Alchemy) — no per-wallet list needed to run the site. |
| `output/allowlist.json` | The authoritative per-wallet mint list (every holder of every eligible collection). Feed this to your mint allowlist / OpenSea allowlist. |
| `output/allowlist-wallets.txt` | Flat newline-separated wallet list, same data. |

## How "trending" and "featured" are defined

OpenSea's public API has no editorial "featured" endpoint, so we use two
rankings of `/api/v2/collections`:

- **trending** → `order_by=seven_day_volume`
- **featured** → `order_by=market_cap` (established / blue collections)

Override via `OPENSEA_TRENDING_ORDER` / `OPENSEA_FEATURED_ORDER` if OpenSea
changes the accepted values. Counts via `TRENDING_COUNT` / `FEATURED_COUNT`.

## Notes

- Without `OPENSEA_API_KEY`, `npm run snapshot` keeps the existing collection
  list and only refreshes missing images (handy for a quick image backfill).
- The holder snapshot paginates `getOwnersForContract` for all ~40 collections;
  for large collections this can be hundreds of thousands of wallets and take a
  while. Re-run before mint to keep it fresh.
