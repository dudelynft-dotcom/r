"""
Perceptual-hash dedup pass.

AI generation can produce near-identical images even when trait DNA differs.
This finds visual collisions (Hamming distance <= threshold on a pHash) and
lists the token_ids that should be re-rendered with a fresh seed.

Run after generate.py; feed the printed ids back into generate.py via a
regenerate loop (delete those PNGs, bump the seed, re-run).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image
import imagehash

ROOT = Path(__file__).resolve().parent.parent
IMG_DIR = ROOT / "output" / "images"
REPORT = ROOT / "output" / "dedup_report.json"


def phash(path: Path) -> imagehash.ImageHash:
    with Image.open(path) as im:
        return imagehash.phash(im.convert("RGB"), hash_size=16)


def find_collisions(threshold: int = 4) -> list[list[int]]:
    images = sorted(IMG_DIR.glob("*.png"), key=lambda p: int(p.stem))
    hashes: list[tuple[int, imagehash.ImageHash]] = []
    for p in images:
        try:
            hashes.append((int(p.stem), phash(p)))
        except Exception as e:  # noqa: BLE001
            print(f"  ! skip {p.name}: {e}")

    # bucket by hash prefix to avoid O(n^2) over all pairs
    groups: list[list[int]] = []
    used: set[int] = set()
    for i, (tid_a, h_a) in enumerate(hashes):
        if tid_a in used:
            continue
        cluster = [tid_a]
        for tid_b, h_b in hashes[i + 1:]:
            if tid_b in used:
                continue
            if (h_a - h_b) <= threshold:
                cluster.append(tid_b)
                used.add(tid_b)
        if len(cluster) > 1:
            used.add(tid_a)
            groups.append(sorted(cluster))
    return groups


def main():
    p = argparse.ArgumentParser(description="Find near-duplicate renders")
    p.add_argument("--threshold", type=int, default=4)
    args = p.parse_args()

    groups = find_collisions(args.threshold)
    # keep the first (usually lowest id) in each cluster, flag the rest
    to_regen = sorted(tid for g in groups for tid in g[1:])
    REPORT.write_text(
        json.dumps({"clusters": groups, "regenerate": to_regen}, indent=2),
        encoding="utf-8",
    )
    print(f"[OK] {len(groups)} collision clusters, {len(to_regen)} tokens to "
          f"regenerate -> {REPORT}")
    if to_regen:
        print("  regenerate ids:", to_regen[:50], "..." if len(to_regen) > 50 else "")


if __name__ == "__main__":
    main()
