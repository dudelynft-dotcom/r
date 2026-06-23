"""
Pin the images and/or metadata folders to IPFS via Pinata.

Set PINATA_JWT (https://app.pinata.cloud > API Keys). Returns the folder CID,
which you then pass to `metadata.py --image-cid ipfs://<CID>` and finally set as
the contract baseURI.

    python -m src.pin_ipfs --dir output/images
    python -m src.pin_ipfs --dir output/metadata
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

import requests

PINATA_URL = "https://api.pinata.cloud/pinning/pinFileToIPFS"


def pin_directory(folder: Path) -> str:
    jwt = os.environ.get("PINATA_JWT")
    if not jwt:
        raise SystemExit("Set PINATA_JWT env var (Pinata API key, JWT).")

    files = []
    for p in sorted(folder.rglob("*")):
        if p.is_file():
            rel = p.relative_to(folder.parent).as_posix()
            files.append(("file", (rel, p.open("rb"))))

    if not files:
        raise SystemExit(f"No files found under {folder}")

    print(f"Pinning {len(files)} files from {folder} ...")
    resp = requests.post(
        PINATA_URL,
        files=files,
        headers={"Authorization": f"Bearer {jwt}"},
        timeout=600,
    )
    resp.raise_for_status()
    cid = resp.json()["IpfsHash"]
    print(f"[OK] pinned -> ipfs://{cid}")
    return cid


def main():
    p = argparse.ArgumentParser(description="Pin a folder to IPFS (Pinata)")
    p.add_argument("--dir", type=Path, required=True)
    args = p.parse_args()
    pin_directory(args.dir)


if __name__ == "__main__":
    main()
