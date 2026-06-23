#!/usr/bin/env python3
# Snapshot every holder of the 25 eligible collections -> CSV + count.
# Uses curl (works where Node fetch/undici is sandbox-blocked).
import json, os, subprocess, time, sys

KEY = os.environ.get("ALCHEMY_API_KEY", "").strip()
if not KEY:
    sys.exit("ALCHEMY_API_KEY not set")

ROOT = os.path.dirname(os.path.abspath(__file__))
WL = os.path.join(ROOT, "..", "web", "data", "whitelist-collections.json")
OUT_DIR = os.path.join(ROOT, "output")
os.makedirs(OUT_DIR, exist_ok=True)

data = json.load(open(WL, encoding="utf-8"))
cols = (data.get("trending") or []) + (data.get("featured") or [])

def curl(url):
    return subprocess.run(["curl", "-s", "--max-time", "60", url],
                          capture_output=True, text=True).stdout

def owners_of(addr):
    out = set()
    page = None
    pages = 0
    while True:
        url = f"https://eth-mainnet.g.alchemy.com/nft/v3/{KEY}/getOwnersForContract?contractAddress={addr}"
        if page:
            url += f"&pageKey={page}"
        body = curl(url)
        try:
            d = json.loads(body)
        except Exception:
            time.sleep(1.0);
            body = curl(url)
            d = json.loads(body)
        for o in d.get("owners", []):
            out.add(str(o).lower())
        page = d.get("pageKey")
        pages += 1
        if not page or pages > 5000:
            break
    return out

all_wallets = set()
per = {}
for i, c in enumerate(cols, 1):
    name, addr = c.get("name", "?"), c["address"]
    try:
        o = owners_of(addr)
    except Exception as e:
        print(f"[{i}/{len(cols)}] {name[:24]:<24} ERROR {e}", flush=True)
        per[name] = 0
        continue
    per[name] = len(o)
    all_wallets |= o
    print(f"[{i}/{len(cols)}] {name[:24]:<24} {len(o):>7} owners | union {len(all_wallets):>7}", flush=True)

# write CSV
csv_path = os.path.join(OUT_DIR, "snapshot-wallets.csv")
with open(csv_path, "w", encoding="utf-8", newline="") as f:
    f.write("wallet\n")
    for w in sorted(all_wallets):
        f.write(w + "\n")

# per-collection breakdown
with open(os.path.join(OUT_DIR, "snapshot-breakdown.json"), "w", encoding="utf-8") as f:
    json.dump({"generatedAt": data.get("generatedAt"),
               "totalUniqueWallets": len(all_wallets),
               "collectionCount": len(cols),
               "perCollection": per}, f, indent=2, ensure_ascii=False)

print("\n========================================")
print(f"TOTAL UNIQUE ELIGIBLE WALLETS: {len(all_wallets):,}")
print(f"CSV: {csv_path}")
print("========================================")
