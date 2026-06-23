# ROBARK — Trait & Art Generation (RunPod)

Generates the full **10,000-piece** collection: unique trait DNA → AI-rendered
pixel-Shiba images on a RunPod GPU (ComfyUI / Stable Diffusion) → OpenSea
metadata + rarity ranking.

## Pipeline

```
traits.yaml ──► src/traits.py ──► output/dna.json        (10k unique combos + rarity)   [CPU]
dna.json    ──► src/generate.py ─► output/images/*.png   (ComfyUI on GPU)                [GPU]
images      ──► src/dedup.py ────► output/dedup_report   (flag near-duplicates)          [CPU]
dna.json    ──► src/metadata.py ─► output/metadata/*.json + rarity_ranking.json          [CPU]
images/meta ──► src/pin_ipfs.py ─► IPFS CIDs (Pinata)                                     [net]
```

The trait/metadata steps need **no GPU** and run anywhere. Only image rendering
needs the RunPod GPU.

## Local (no GPU) — produce the traits now
```bash
pip install -r requirements.txt
python -m src.traits --size 10000          # -> output/dna.json + rarity_report.json
python -m src.metadata --image-cid ipfs://PLACEHOLDER
```

## On a RunPod GPU pod
1. Launch a **ComfyUI** template pod (A100/4090). Expose port `8188`.
2. Put a pixel-art checkpoint in `ComfyUI/models/checkpoints/` and update the
   `ckpt_name` in [`workflows/pixel_shiba.json`](workflows/pixel_shiba.json).
   (Export your own workflow from the ComfyUI UI in **API format** and keep the
   node ids in sync with `COMFY_NODE_*` env / `src/comfy_client.py`.)
3. Run the whole thing:
   ```bash
   export COMFY_URL=http://127.0.0.1:8188
   bash run.sh
   ```
   Render across multiple pods by sharding: `SHARDS=4 SHARD=0 bash run.sh` … `SHARD=3`.

### Serverless alternative
`runpod_handler.py` is a RunPod Serverless handler that renders batches of token
ids and returns base64 PNGs — use it if you prefer autoscaling over a pod.

## Customising the art
Everything about the look is data: edit [`traits/traits.yaml`](traits/traits.yaml)
to add/rename traits, change rarity `weight`s, or tweak the `prompt` fragments
the GPU renders. The whole collection re-derives deterministically from the seed.

## Outputs (`output/`, git-ignored)
- `dna.json` — every token's traits, dna hash, rarity score & rank
- `rarity_report.json` — trait frequency table
- `images/<id>.png` — rendered art
- `metadata/<id>.json` — ERC-721 metadata (OpenSea standard)
- `rarity_ranking.json` — tokens sorted by rarity
- `merkle`/pins as you proceed

## Reveal flow
Generate → pin images (`pin_ipfs.py --dir output/images`) → re-run `metadata.py
--image-cid ipfs://<CID>` → pin metadata → set the contract `baseURI` to the
metadata CID.
