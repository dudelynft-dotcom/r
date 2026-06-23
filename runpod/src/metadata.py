"""
Build OpenSea-standard metadata for every token + a rarity ranking file.

Reads output/dna.json, writes:
  output/metadata/<token_id>.json   (one per token, ERC-721 metadata)
  output/metadata/_collection.json  (collection-level)
  output/rarity_ranking.json        (sorted by rarity)

The image field uses an ipfs:// base you pass with --image-cid (the CID of the
folder of images pinned to IPFS). Reveal by swapping a placeholder base for the
real CID after mint.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .traits import Taxonomy, Token, compute_rarity

ROOT = Path(__file__).resolve().parent.parent
DNA_FILE = ROOT / "output" / "dna.json"
META_DIR = ROOT / "output" / "metadata"


def load_tokens() -> list[Token]:
    data = json.loads(DNA_FILE.read_text(encoding="utf-8"))
    toks = []
    for d in data:
        t = Token(token_id=d["token_id"], traits=d["traits"], dna=d["dna"])
        t.rarity_score = d.get("rarity_score", 0.0)
        t.rank = d.get("rank", 0)
        toks.append(t)
    return toks


def token_metadata(tax: Taxonomy, t: Token, image_base: str, ext: str = "png") -> dict:
    attributes = [
        {"trait_type": layer, "value": value}
        for layer, value in t.traits.items()
    ]
    attributes.append({"trait_type": "Rarity Rank", "value": t.rank,
                       "display_type": "number"})
    return {
        "name": f"{tax.name} #{t.token_id}",
        "description": (
            f"{tax.name} is a collection of {tax.size} pixel-bred Shibas on "
            "Ethereum. All blue. All degen."
        ),
        "image": f"{image_base.rstrip('/')}/{t.token_id}.{ext}",
        "attributes": attributes,
        "robark": {
            "dna": t.dna,
            "rarity_score": t.rarity_score,
            "rank": t.rank,
        },
    }


def main():
    p = argparse.ArgumentParser(description="Build ROBARK metadata")
    p.add_argument("--image-cid", default="ipfs://REPLACE_WITH_IMAGE_FOLDER_CID",
                   help="ipfs:// base for the images folder")
    p.add_argument("--ext", default="png")
    args = p.parse_args()

    tax = Taxonomy.load()
    tokens = load_tokens()
    compute_rarity(tax, tokens)  # ensure ranks are fresh

    META_DIR.mkdir(parents=True, exist_ok=True)
    for t in tokens:
        meta = token_metadata(tax, t, args.image_cid, args.ext)
        (META_DIR / f"{t.token_id}.json").write_text(
            json.dumps(meta, indent=2), encoding="utf-8"
        )

    collection = {
        "name": tax.name,
        "description": f"{tax.size} pixel-bred Shibas on Ethereum. All blue.",
        "image": f"{args.image_cid.rstrip('/')}/0.{args.ext}",
        "seller_fee_basis_points": 500,
        "external_link": "https://robark.io",
    }
    (META_DIR / "_collection.json").write_text(
        json.dumps(collection, indent=2), encoding="utf-8"
    )

    ranking = [
        {"token_id": t.token_id, "rank": t.rank, "rarity_score": t.rarity_score,
         "traits": t.traits}
        for t in sorted(tokens, key=lambda x: x.rank)
    ]
    (ROOT / "output" / "rarity_ranking.json").write_text(
        json.dumps(ranking, indent=2), encoding="utf-8"
    )

    print(f"[OK] wrote {len(tokens)} metadata files -> {META_DIR}")
    print(f"[OK] rarity ranking -> output/rarity_ranking.json")


if __name__ == "__main__":
    main()
