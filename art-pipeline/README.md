# ROBARK — Art Pipeline

The real ROBARK collection: **10,000 hand-drawn degen dogs** who survived the
crash. Same dog, same handmade hand — **9 trait layers recombine** so every piece
is different (see [`TRAITS.md`](TRAITS.md) for the full trait bible).

> **Style law:** pure hand-drawn / OK-Guy energy — thick wobbly marker outlines,
> flat felt-tip fills, naive doodle proportions. It must look **made by a human,
> never AI**. Enforced in every prompt (`traits.yaml` → `style`) and an optional
> OCR no-text guard.

```
traits.yaml ─► src/dna.py ─────► output/dna.json    (10k unique trait combos + prompt + seed + rarity)  [CPU]
dna.json    ─► src/generate.py ─► output/images/*.png  (full hand-drawn render per token)   [fal / RunPod GPU]
dna.json    ─► src/metadata.py ─► output/metadata/*.json + rarity_ranking.json              [CPU]
```

## Workflow (your plan)
1. **Samples on fal.ai** — perfect the style on ~8 images, cheap and fast.
2. **Full 10k on RunPod** — same prompts + a **ROBARK character LoRA** for perfect
   consistency. See [`RUNPOD.md`](RUNPOD.md).

```bash
pip install -r requirements.txt
# put FAL_KEY in web/.env.local (or export it) and top up fal credits
python -m src.dna --size 10000          # build trait DNA + prompts (no GPU)
python -m src.generate --count 8        # render the first 8 as style samples (fal)
python -m src.metadata --image-cid ipfs://<CID>
```

## Traits
- Human-readable spec with every variant + how it looks: [`TRAITS.md`](TRAITS.md)
- Machine-readable weights + prompt fragments: [`traits.yaml`](traits.yaml)
- 9 layers: **Background, Fur, Eyes, Mouth, Eyewear, Headwear, Outfit, Chain,
  Accessory** (+ a handful of 1/1 Legendaries). Edit weights to tune rarity.
- All backgrounds are **strictly text-free** (no words/letters/signs/logos).

## No text + no AI look — enforced
- Every prompt ends with a hard anti-AI / no-text guard (FLUX has no negative field).
- `src/generate.py` has an optional **OCR guard**: with `pytesseract` (+ tesseract
  binary) installed, any render containing text is regenerated with a new seed.

## Assets
`assets/robark_character.png` — the master ROBARK cut out of the original art
(OpenCV GrabCut). Used as the LoRA reference / fallback hero art.

## Outputs (`output/`, git-ignored)
`dna.json` · `images/<id>.png` (final NFTs) · `metadata/<id>.json` ·
`rarity_ranking.json`

## Cost
~10,000 renders. Validate on fal with `--count 8`, then do the full batch on a
RunPod pod with the LoRA (cheaper per image at scale). Top up: fal.ai/dashboard/billing.
