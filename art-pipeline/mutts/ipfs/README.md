# ROBARK → IPFS without Pinata

Three free ways to host the 5,555 on IPFS. Pick one. The flow is the same:
**upload images folder → get folder CID → `set_cid.py` → upload metadata folder
→ metadata CID = your contract baseURI (or OpenSea metadata).**

Your files: `art-pipeline/mutts/output/images/` (PNGs) and `output/metadata/` (JSON).

---

## Option 0 — Pinata free tier (simple web UI, fine for this size)
Collection is ~31 MB (PNG + metadata) vs Pinata's 1 GB free — plenty.
1. Sign up free at pinata.cloud.
2. **Files → Upload → Folder** → `output/images` → copy the **images folder CID**.
3. `python art-pipeline/mutts/ipfs/set_cid.py --cid <IMAGES_CID> --ext png`
4. **Upload → Folder** → `output/metadata` → **metadata CID = baseURI** `ipfs://<CID>/`.
Notes: use PNG (23 MB) not SVG (133 MB); upload as folders; OpenSea caches images
so Pinata's free gateway bandwidth limit is a non-issue for a collection this small.

## Option A — web3.storage (Storacha) ⭐ recommended, free
Decentralized, free tier, no Pinata. Uses the `w3` CLI.
```bash
npm install -g @web3-storage/w3cli
w3 login you@email.com            # click the email link to verify
w3 space create robark            # one-time space
# 1) upload the images folder
w3 up art-pipeline/mutts/output/images
#   -> prints:  https://<CID>.ipfs.w3s.link   (the <CID> is your IMAGES folder CID)

# 2) write that CID into every metadata file
python art-pipeline/mutts/ipfs/set_cid.py --cid <IMAGES_CID> --ext png

# 3) upload the metadata folder
w3 up art-pipeline/mutts/output/metadata
#   -> <METADATA_CID>  ->  baseURI = ipfs://<METADATA_CID>/
```

## Option B — Lighthouse (perpetual storage, free tier)
```bash
npm install -g lighthouse-web3
lighthouse-web3 create-wallet      # or import; get an API key at files.lighthouse.storage
lighthouse-web3 upload art-pipeline/mutts/output/images   # -> IMAGES_CID
python art-pipeline/mutts/ipfs/set_cid.py --cid <IMAGES_CID> --ext png
lighthouse-web3 upload art-pipeline/mutts/output/metadata # -> METADATA_CID
```

## Option C — fully self-hosted (no third party at all) via Kubo
You run your own IPFS node. Free, but the files stay available only while a node
that has them is online — so keep this node (or a cheap VPS) running, or remote-pin
to a free service.
```bash
# install IPFS Kubo: https://docs.ipfs.tech/install/command-line/
ipfs init
ipfs add -r --cid-version 1 art-pipeline/mutts/output/images   # last line = IMAGES_CID
python art-pipeline/mutts/ipfs/set_cid.py --cid <IMAGES_CID> --ext png
ipfs add -r --cid-version 1 art-pipeline/mutts/output/metadata  # -> METADATA_CID
ipfs daemon                                                     # keep running to serve
# (optional) pre-compute the CID without keeping data:  ipfs add -rn --cid-version 1 output/images
```

---

## Notes
- **SVG instead of PNG?** Upload `output/svg` and run `set_cid.py --ext svg`.
- **Verify** any CID in a browser: `https://<CID>.ipfs.w3s.link/0.png` or
  `https://ipfs.io/ipfs/<CID>/0.png`.
- For OpenSea, set the contract's `tokenURI`/`baseURI` to `ipfs://<METADATA_CID>/`
  (token `i` → `ipfs://<METADATA_CID>/i.json`). If your metadata files need a
  `.json` suffix in the URI, they already are named `<id>.json`.
