"""
OpenSea-standard metadata + rarity ranking for the full ROBARK collection.
Traits come straight from each token's DNA (the 9 layers) plus a derived tier.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DNA = ROOT / "output" / "dna.json"
META_DIR = ROOT / "output" / "metadata"

TRAIT_ORDER = ["Background", "Fur", "Eyes", "Mouth", "Eyewear",
               "Headwear", "Outfit", "Chain", "Accessory"]


def tier_for(rank: int, total: int) -> str:
    pct = rank / total
    if pct <= 0.005:
        return "Mythic"
    if pct <= 0.05:
        return "Legendary"
    if pct <= 0.15:
        return "Epic"
    if pct <= 0.4:
        return "Rare"
    return "Common"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image-cid", default="ipfs://REPLACE_WITH_IMAGE_FOLDER_CID")
    ap.add_argument("--ext", default="png")
    args = ap.parse_args()

    toks = json.loads(DNA.read_text(encoding="utf-8"))
    total = len(toks)
    META_DIR.mkdir(parents=True, exist_ok=True)
    base = args.image_cid.rstrip("/")

    for t in toks:
        tier = tier_for(t["rank"], total)
        attrs = [{"trait_type": k, "value": t["traits"][k]} for k in TRAIT_ORDER if k in t["traits"]]
        attrs.append({"trait_type": "Rarity Tier", "value": tier})
        attrs.append({"trait_type": "Rarity Rank", "value": t["rank"], "display_type": "number"})
        meta = {
            "name": f"ROBARK #{t['token_id']}",
            "description": (
                "ROBARK survived the crash. 10,000 hand-drawn degens on Ethereum — "
                "one iconic dog, 10,000 different bad days. Lost everything, still bullish."
            ),
            "image": f"{base}/{t['token_id']}.{args.ext}",
            "attributes": attrs,
            "robark": {"seed": t["seed"], "dna": t["dna"],
                       "rarity_score": t["rarity_score"], "rank": t["rank"]},
        }
        (META_DIR / f"{t['token_id']}.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    (META_DIR / "_collection.json").write_text(json.dumps({
        "name": "ROBARK",
        "description": "10,000 hand-drawn degens who survived the crash.",
        "image": f"{base}/0.{args.ext}",
        "seller_fee_basis_points": 500,
        "external_link": "https://robark.io",
    }, indent=2), encoding="utf-8")

    ranking = [
        {"token_id": t["token_id"], "rank": t["rank"], "rarity_score": t["rarity_score"],
         "tier": tier_for(t["rank"], total), "traits": t["traits"]}
        for t in sorted(toks, key=lambda x: x["rank"])
    ]
    (ROOT / "output" / "rarity_ranking.json").write_text(json.dumps(ranking, indent=2), encoding="utf-8")
    print(f"[OK] {total} metadata files -> {META_DIR}")
    print(f"[OK] rarity ranking -> output/rarity_ranking.json")


if __name__ == "__main__":
    main()
