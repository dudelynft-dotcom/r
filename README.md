# 🐕 ROBARK.IO

**The 24-Hour Degen Mint** — 10,000 pixel-bred Shibas on Ethereum. No whitelist
forms. We snapshot the whole chain; if you hold, you're in.

This monorepo contains everything for the drop:

| Folder | What it is | Stack |
| --- | --- | --- |
| [`web/`](web/) | The professional, fully-blue website: landing page + **whitelist checker** (paste an address & search — no wallet connect). Mint happens on **OpenSea**. | Next.js 14, Tailwind, Alchemy |
| [`runpod/`](runpod/) | The **10,000-trait generation pipeline** — trait DNA + AI image rendering on a RunPod GPU (ComfyUI/Stable Diffusion) + metadata + rarity. | Python, ComfyUI API |
| [`snapshot/`](snapshot/) | The **chain snapshot** — indexes NFT holders via Alchemy, applies the eligibility rules, and outputs the allowlist + Merkle roots. | Node, Alchemy API |

---

## The mint at a glance

- **Supply:** 10,000 · **Window:** 24 hours · **Mint on:** OpenSea
- **Phase 1 — Bluechip** (0–8h): hold **10+ NFTs** *and* a verified **bluechip**, each collection floor **> $10** in ETH.
- **Phase 2 — Degen** (8–16h): hold **10+ NFTs** with floor **> $10** in ETH.
- **Phase 3 — Public** (16–24h): open to everyone.

Eligibility thresholds live in one place per app and are mirrored:
`web/lib/config.ts` ⇄ `snapshot/lib/config.js`.

---

## Quickstart

### 1. Website
```bash
cd web
npm install
cp .env.example .env.local      # add ALCHEMY_API_KEY
npm run dev                     # http://localhost:3000
```
The checker works in **demo mode** with no keys; add `ALCHEMY_API_KEY` for live
on-chain results, or drop a snapshot `allowlist.json` into `web/data/`.

### 2. Generate the 10,000 traits
```bash
cd runpod
pip install -r requirements.txt
python -m src.traits --size 10000        # trait DNA + rarity (CPU, no GPU)
# then on a RunPod GPU pod with ComfyUI:
bash run.sh                               # renders images + metadata
```

### 3. Snapshot the chain → allowlist
```bash
cd snapshot
npm install
ALCHEMY_API_KEY=xxx node snapshot.js --block <BLOCK> --max-wallets 5000
cp output/allowlist.json ../web/data/allowlist.json
```

See each folder's README for full details.

---

## Art

The demo art (pixel Shiba on blue) sets the palette and style. Drop the real
hero art at `web/public/art/hero.png`. The whole site is locked to the blue
theme sampled from it (`web/tailwind.config.ts`).

> Not financial advice. DYOR.
