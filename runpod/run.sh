#!/usr/bin/env bash
# End-to-end ROBARK generation on a RunPod GPU pod.
# Assumes a ComfyUI image with the pod's ComfyUI serving on :8188 and a
# pixel-art checkpoint placed in ComfyUI/models/checkpoints/.
set -euo pipefail

cd "$(dirname "$0")"

export COMFY_URL="${COMFY_URL:-http://127.0.0.1:8188}"

echo "==> [1/5] Installing pipeline deps"
pip install -q -r requirements.txt

echo "==> [2/5] Generating 10,000 trait DNA + rarity"
python -m src.traits --size 10000

echo "==> [3/5] Rendering images via ComfyUI ($COMFY_URL)"
# Shard across multiple pods by setting SHARD / SHARDS, e.g. SHARD=0 SHARDS=4
if [[ -n "${SHARDS:-}" ]]; then
  python -m src.generate --shard "${SHARD:-0}" --shards "$SHARDS"
else
  python -m src.generate --start 0 --count 10000
fi

echo "==> [4/5] Dedup pass (flag near-duplicate renders)"
python -m src.dedup --threshold 4 || true

echo "==> [5/5] Building metadata"
# Pin images first, then pass the CID here. Placeholder kept for pre-reveal.
python -m src.metadata --image-cid "${IMAGE_CID:-ipfs://REPLACE_WITH_IMAGE_FOLDER_CID}"

echo "==> Done. Outputs in ./output (images/, metadata/, rarity_ranking.json)"
echo "    Next: python -m src.pin_ipfs --dir output/images   # then re-run metadata with the CID"
