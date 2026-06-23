"""
Pin a folder to IPFS via Pinata (reads JWT from web/.env.local). Pins the whole
directory in one request and prints the folder CID, where files are served at
ipfs://<CID>/<name>.

    python pin_pinata.py ../output/images
    python pin_pinata.py ../output/metadata
"""
from __future__ import annotations
import sys
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[3]          # ROBARK.IO/
ENV = ROOT / "web" / ".env.local"
URL = "https://api.pinata.cloud/pinning/pinFileToIPFS"


def jwt() -> str:
    for line in ENV.read_text(encoding="utf-8").splitlines():
        if "pinata_jwt" in line.lower():
            return line.split("=", 1)[1].strip()
    sys.exit("pinata_jwt not found in web/.env.local")


def pin_folder(folder: Path) -> str:
    files = []
    for p in sorted(folder.iterdir(), key=lambda x: x.name):
        if p.is_file():
            files.append(("file", (f"{folder.name}/{p.name}", p.read_bytes(), "application/octet-stream")))
    print(f"Pinning {len(files)} files from {folder.name} ...")
    r = requests.post(
        URL, files=files,
        data={"pinataOptions": '{"cidVersion":1}', "pinataMetadata": f'{{"name":"robark-{folder.name}"}}'},
        headers={"Authorization": f"Bearer {jwt()}"},
        timeout=900,
    )
    r.raise_for_status()
    cid = r.json()["IpfsHash"]
    print(f"[OK] {folder.name} -> ipfs://{cid}")
    print(f"     check: https://gateway.pinata.cloud/ipfs/{cid}/{files[0][1][0].split('/')[-1]}")
    return cid


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else (ROOT / "art-pipeline/mutts/output/images")
    pin_folder(target.resolve())
