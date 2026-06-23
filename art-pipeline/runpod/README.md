# ROBARK — Full Collection Render on RunPod

Renders all **5,555** ROBARK in the **exact approved style** (see
`art-previews/STYLE_LOCKED/`) — same recipe as the fal samples, but local and
cheap at scale:

> **FLUX.1-dev + canny ControlNet (locks the FINAL pose) + Flux-Sketch-Flat LoRA**

fal was perfect for dialing it in; RunPod is for the 5,555 batch.

---

## ⚡ 2-GPU split (2,778 + 2,777) — recommended, ~2× faster

The trait DNA is shared (built once locally); each pod renders half. Because the
job is resumable and image filenames are the token id, the two halves just drop
into the same `images/` folder with no collisions.

**On both pods:** clone the repo, then:
```bash
cd art-pipeline/runpod
bash setup.sh
huggingface-cli login          # paste HF token (accept FLUX.1-dev license first)
```

**Pod A (GPU 1):**
```bash
python generate_flat.py --start 0 --count 2778        # tokens 0–2777
```
**Pod B (GPU 2):**
```bash
python generate_flat.py --start 2778 --count 2777     # tokens 2778–5554
```
Add `--offload` on either if the GPU is < 40 GB (e.g. RTX 4090). When both finish,
collect each pod's `output/collection/images/*.png` into one folder = all 5,555.

> Want 3–4 GPUs? Same idea: split 5555 into N ranges (e.g. 4×≈1389).

---

## Full flow

1. **Locally (no GPU)** — build the trait DNA + metadata (already done):
   ```bash
   cd art-pipeline
   python -m src.collection --size 5555 --dna-only
   # -> output/collection/_dna.json  (+ metadata/*.json, rarity_ranking via metadata.py)
   ```
2. **Push the repo** to both pods (git clone / runpodctl / network volume). The
   pods need `art-pipeline/output/collection/_dna.json` and
   `art-previews/FINAL/08_degen_trenches.png`.
3. **Render** with the 2-GPU split above.
4. **Collect** all images into `output/collection/images/`.
5. **Metadata is already generated** locally (`output/collection/metadata/`).
   After pinning images to IPFS, set the image CID:
   ```bash
   python -m src.metadata --image-cid ipfs://<IMAGES_CID>   # (collection metadata builder)
   ```

## GPU notes
- **A100 80GB**: best, run without `--offload`. ~3–6 s/image → 2,778 imgs ≈ 2–5 h/pod.
- **RTX 4090 / A40 (24–48GB)**: use `--offload`; slower but works.
- First run downloads FLUX.1-dev (~24GB) + ControlNet + LoRA. Use a **network
  volume** so both pods share the cache and you don't re-download.

## Matching the fal look (tunables in `generate_flat.py`)
- `CONTROL_SCALE = 0.60` — structure lock (higher = tighter to the FINAL pose).
- `LORA_SCALE = 1.05` — flat-style strength.
- `STEPS = 28`, `GUIDANCE = 3.5`. Render the first ~20 and eyeball vs
  `art-previews/STYLE_LOCKED/`; nudge CONTROL_SCALE ±0.1 if pose/colors drift.

## No-text cleanup
FLUX occasionally adds a background sign. Install tesseract on the pod
(`apt-get install -y tesseract-ocr && pip install pytesseract`) and the existing
OCR guard logic can flag text pieces for a quick re-roll, or cull them by eye in
the final QA pass.
