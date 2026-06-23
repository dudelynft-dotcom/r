# Completing the full 10k on RunPod

fal.ai is perfect for **dialing in the style on a few samples** cheaply. For the
full collection you move to a **RunPod GPU pod** — same prompts, but with a
**ROBARK character LoRA** so the dog is perfectly on-model and consistently
hand-drawn across all 10,000 (text-to-image alone drifts).

## The plan

### 1. Lock the look on fal (cheap, fast)
```bash
# (top up fal credits first)
python -m src.dna --size 10000
python -m src.generate --count 8          # render the first 8 as style samples
```
Iterate on `traits.yaml` `style` / `base_character` until 8/8 look hand-drawn and
on-brand. This is the cheap loop — keep it here until you love it.

### 2. Train the ROBARK LoRA (RunPod, one-time)
You need the character consistent. Train a small LoRA on the master:
1. Build a tiny dataset: 10–20 images of ROBARK in different poses/traits, all in
   the handmade style (use your best fal samples + the master art, lightly varied).
   Caption each like: `ROBARK, a hand-drawn cartoon degen dog, <traits>`.
2. On a RunPod pod (e.g. **A100 / 4090**, "FLUX training" or `ai-toolkit` /
   `kohya_ss` template), train a FLUX LoRA on that set (~1000–2000 steps). Trigger
   word: `ROBARK`.
3. Save `robark_lora.safetensors`.

### 3. Render all 10k on RunPod with the LoRA
Two easy options on the pod:

**a) ComfyUI** (recommended) — load FLUX + the LoRA, drive it with our prompts.
The repo already has a Comfy client in `../runpod/src/comfy_client.py`; point it
at this pipeline's `output/dna.json` prompts, or:

**b) `fal` model swap** — fal also hosts `fal-ai/flux-lora`; upload the LoRA and
set the model so the SAME `src/generate.py` runs it:
```bash
export FAL_MODEL="fal-ai/flux-lora"        # then pass loras=[{path,scale}] in the payload
python -m src.generate --start 0 --count 10000
```
(For the LoRA payload, add `"loras": [{"path": "<lora-url>", "scale": 1.0}]` to the
`fal()` payload in `src/generate.py`.)

### 4. Finish
```bash
python -m src.metadata --image-cid ipfs://<images-cid>
# dedup near-identical renders (reuse ../runpod/src/dedup.py), then pin to IPFS
```

## Why LoRA over plain prompting
- **Consistency:** every ROBARK is unmistakably the same dog.
- **Style lock:** the handmade, non-AI look is baked into the model, not just the
  prompt — far fewer "too clean / too AI" rejects.
- **Speed/cost:** a 4090/A100 pod renders 10k in a long batch far cheaper per image
  than per-call API pricing.

## Keeping it hand-drawn (anti-AI checklist)
- Trigger the LoRA every prompt; keep `guidance_scale` low (~3.0) for flatter fills.
- Reject anything with smooth gradients / 3D sheen (eyeball the first 200).
- Keep the OCR no-text guard ON (`pip install pytesseract` + the tesseract binary).
