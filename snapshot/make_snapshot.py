#!/usr/bin/env python3
# Snapshot holders of the 25 eligible collections.
# Outputs:
#   web/data/snapshot.json          -> { generatedAt, walletCount, collections[], wallets{addr:[idx]} }
#   snapshot/output/snapshot-wallets.csv
#   snapshot/output/snapshot-breakdown.json
# Uses curl (works where Node fetch/undici is sandbox-blocked).
import json, os, subprocess, time, sys

KEY = os.environ.get("ALCHEMY_API_KEY", "").strip()
if not KEY:
    sys.exit("ALCHEMY_API_KEY not set")

ROOT = os.path.dirname(os.path.abspath(__file__))
WL = os.path.join(ROOT, "..", "web", "data", "whitelist-collections.json")
WEB_SNAP = os.path.join(ROOT, "..", "web", "data", "snapshot.json")
OUT_DIR = os.path.join(ROOT, "output")
os.makedirs(OUT_DIR, exist_ok=True)

BURNS = {
    "0x0000000000000000000000000000000000000000",
    "0x000000000000000000000000000000000000dead",
}

data = json.load(open(WL, encoding="utf-8"))
cols = (data.get("trending") or []) + (data.get("featured") or [])
collections = [{"address": c["address"].lower(), "name": c.get("name", "?"), "image": c.get("image")} for c in cols]

def curl(url):
    return subprocess.run(["curl", "-s", "--max-time", "60", url], capture_output=True, text=True).stdout

def owners_of(addr):
    out, page, pages = set(), None, 0
    while True:
        url = f"https://eth-mainnet.g.alchemy.com/nft/v3/{KEY}/getOwnersForContract?contractAddress={addr}"
        if page:
            url += f"&pageKey={page}"
        body = curl(url)
        try:
            d = json.loads(body)
        except Exception:
            time.sleep(1.0); d = json.loads(curl(url))
        for o in d.get("owners", []):
            w = str(o).lower()
            if w not in BURNS:
                out.add(w)
        page = d.get("pageKey"); pages += 1
        if not page or pages > 5000:
            break
    return out

wallets = {}          # addr -> set(idx)
per = {}
for i, c in enumerate(collections):
    try:
        owners = owners_of(c["address"])
    except Exception as e:
        print(f"[{i+1}/{len(collections)}] {c['name'][:24]:<24} ERROR {e}", flush=True)
        per[c["name"]] = 0; continue
    per[c["name"]] = len(owners)
    for w in owners:
        wallets.setdefault(w, set()).add(i)
    print(f"[{i+1}/{len(collections)}] {c['name'][:24]:<24} {len(owners):>7} | union {len(wallets):>7}", flush=True)

# web snapshot (compact: indices)
snap = {
    "generatedAt": data.get("generatedAt"),
    "walletCount": len(wallets),
    "collections": collections,
    "wallets": {w: sorted(idx) for w, idx in wallets.items()},
}
json.dump(snap, open(WEB_SNAP, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))

# CSV + breakdown
with open(os.path.join(OUT_DIR, "snapshot-wallets.csv"), "w", encoding="utf-8", newline="") as f:
    f.write("wallet\n")
    for w in sorted(wallets):
        f.write(w + "\n")
json.dump({"generatedAt": data.get("generatedAt"), "totalUniqueWallets": len(wallets),
           "collectionCount": len(collections), "perCollection": per},
          open(os.path.join(OUT_DIR, "snapshot-breakdown.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)

size_mb = os.path.getsize(WEB_SNAP) / 1e6
print("\n========================================")
print(f"TOTAL UNIQUE ELIGIBLE WALLETS: {len(wallets):,}")
print(f"web/data/snapshot.json: {size_mb:.1f} MB")
print("========================================")
