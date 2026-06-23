"""
End-to-end: DNA -> images (fal/RunPod) -> metadata.

    python -m src.build --size 10000              # full
    python -m src.build --size 10000 --count 8    # just render first 8 (sample)

Stages are independent and resumable:
    python -m src.dna --size 10000
    python -m src.generate --start 0 --count 8
    python -m src.metadata --image-cid ipfs://<CID>
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(mod: str, *args: str):
    cmd = [sys.executable, "-m", mod, *args]
    print(f"\n==> {' '.join(cmd)}")
    subprocess.run(cmd, cwd=ROOT, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=int, default=10000)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--count", type=int, default=None)
    ap.add_argument("--image-cid", default="ipfs://REPLACE_WITH_IMAGE_FOLDER_CID")
    args = ap.parse_args()

    run("src.dna", "--size", str(args.size))
    gen = ["--start", str(args.start)]
    if args.count is not None:
        gen += ["--count", str(args.count)]
    run("src.generate", *gen)
    run("src.metadata", "--image-cid", args.image_cid)
    print("\n[OK] pipeline complete -> art-pipeline/output/images + metadata")


if __name__ == "__main__":
    main()
