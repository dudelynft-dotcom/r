"""
Inject the real IPFS folder CID into all ROBARK metadata files.

After you upload output/images (or output/svg) to IPFS and get the FOLDER CID,
run this to rewrite every metadata file's `image` field from the placeholder
`ipfs://CID/<id>.png` to `ipfs://<your-cid>/<id>.<ext>`.

    python set_cid.py --cid bafybei...your-images-folder-cid --ext png
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
META = ROOT / "output" / "metadata"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cid", required=True, help="the images FOLDER CID from your IPFS upload")
    ap.add_argument("--ext", default="png", choices=["png", "svg"])
    a = ap.parse_args()
    cid = a.cid.replace("ipfs://", "").strip("/")

    n = 0
    for p in sorted(META.glob("*.json"), key=lambda x: int(x.stem)):
        m = json.loads(p.read_text(encoding="utf-8"))
        tid = p.stem
        m["image"] = f"ipfs://{cid}/{tid}.{a.ext}"
        p.write_text(json.dumps(m, indent=2), encoding="utf-8")
        n += 1
    print(f"[OK] set image CID on {n} metadata files -> ipfs://{cid}/<id>.{a.ext}")


if __name__ == "__main__":
    main()
