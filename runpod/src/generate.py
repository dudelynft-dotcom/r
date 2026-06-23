"""
Drive image generation for the whole collection on a RunPod GPU pod.

Reads the trait DNA (output/dna.json), builds a prompt per token, calls ComfyUI
to render it, and saves images/<token_id>.png. Resumable: already-rendered
tokens are skipped, so you can restart after a crash or scale across pods with
--shard.

Usage (on the pod):
    python -m src.generate --start 0 --count 10000
    python -m src.generate --shard 0 --shards 4   # 4 pods in parallel
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from .comfy_client import ComfyClient
from .prompts import build_prompt
from .traits import Taxonomy, Token

ROOT = Path(__file__).resolve().parent.parent
DNA_FILE = ROOT / "output" / "dna.json"
IMG_DIR = ROOT / "output" / "images"


def load_tokens() -> list[Token]:
    data = json.loads(DNA_FILE.read_text(encoding="utf-8"))
    toks = []
    for d in data:
        t = Token(token_id=d["token_id"], traits=d["traits"], dna=d["dna"])
        t.rarity_score = d.get("rarity_score", 0.0)
        t.rank = d.get("rank", 0)
        toks.append(t)
    return toks


def derive_seed(token: Token, base_seed: int = 1_000_000) -> int:
    # deterministic but distinct per token
    return base_seed + int(token.dna[:8], 16) % 2_000_000_000


def main():
    p = argparse.ArgumentParser(description="Render ROBARK collection via ComfyUI")
    p.add_argument("--start", type=int, default=0)
    p.add_argument("--count", type=int, default=None, help="how many from --start")
    p.add_argument("--shard", type=int, default=None, help="this shard index")
    p.add_argument("--shards", type=int, default=None, help="total shards")
    p.add_argument("--retries", type=int, default=2)
    args = p.parse_args()

    tax = Taxonomy.load()
    tokens = load_tokens()
    IMG_DIR.mkdir(parents=True, exist_ok=True)

    if args.shard is not None and args.shards:
        tokens = [t for t in tokens if t.token_id % args.shards == args.shard]
    else:
        end = len(tokens) if args.count is None else args.start + args.count
        tokens = [t for t in tokens if args.start <= t.token_id < end]

    client = ComfyClient()
    done = skipped = failed = 0
    t0 = time.time()

    for t in tokens:
        out = IMG_DIR / f"{t.token_id}.png"
        if out.exists() and out.stat().st_size > 0:
            skipped += 1
            continue

        pos, neg = build_prompt(tax, t)
        seed = derive_seed(t)
        for attempt in range(args.retries + 1):
            try:
                client.generate(pos, neg, seed + attempt, out)
                done += 1
                break
            except Exception as e:  # noqa: BLE001
                if attempt == args.retries:
                    failed += 1
                    print(f"  [X] token {t.token_id} failed: {e}")
                else:
                    time.sleep(2)

        if (done + skipped) % 50 == 0:
            rate = done / max(1e-9, time.time() - t0)
            print(f"  {done} rendered, {skipped} skipped, {failed} failed "
                  f"({rate:.2f}/s)")

    print(f"\n[OK] done={done} skipped={skipped} failed={failed} "
          f"in {time.time() - t0:.0f}s -> {IMG_DIR}")


if __name__ == "__main__":
    main()
