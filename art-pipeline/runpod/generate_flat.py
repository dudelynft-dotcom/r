import argparse, json
from pathlib import Path
import cv2, numpy as np, torch
from PIL import Image
from diffusers import FluxControlNetModel, FluxControlNetPipeline

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = ROOT.parent
DNA = ROOT / "output" / "collection" / "_dna.json"
OUT = ROOT / "output" / "collection" / "images"
FINAL = REPO / "art-previews" / "FINAL" / "08_degen_trenches.png"

BASE_MODEL = "black-forest-labs/FLUX.1-dev"
CONTROLNET = "InstantX/FLUX.1-dev-Controlnet-Canny"
LORA_REPO = "strangerzonehf/Flux-Sketch-Flat-LoRA"
LORA_FILE = "Sketch-Flat.safetensors"

CONTROL_SCALE = 0.65      # locks the HEAD (canny is masked to the top half)
LORA_SCALE = 1.05         # flat hand-drawn style
STEPS = 20
GUIDANCE = 3.5
SIZE = 1024
HEAD_KEEP = 0.50          # keep canny edges in the top 50% (head); free the body/clothing


def finalize(pil):
    """De-grain + crop the cream border so every saved image is final."""
    im = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
    im = cv2.bilateralFilter(im, 9, 75, 75)
    im = cv2.bilateralFilter(im, 9, 75, 75)
    c = im[3:13, 3:13].reshape(-1, 3).mean(0)
    d = np.abs(im.astype(int) - c).sum(2)
    m = cv2.morphologyEx((d > 45).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    ys, xs = np.where(m > 0)
    if len(xs) > 50:
        im = im[ys.min():ys.max()+1, xs.min():xs.max()+1]
    im = cv2.resize(im, (SIZE, SIZE), interpolation=cv2.INTER_AREA)
    return Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))


def build_pipe(offload):
    cn = FluxControlNetModel.from_pretrained(CONTROLNET, torch_dtype=torch.bfloat16)
    pipe = FluxControlNetPipeline.from_pretrained(BASE_MODEL, controlnet=cn, torch_dtype=torch.bfloat16)
    pipe.load_lora_weights(LORA_REPO, weight_name=LORA_FILE)
    pipe.enable_model_cpu_offload() if offload else pipe.to("cuda")
    return pipe


def canny():
    img = cv2.imread(str(FINAL))
    e = cv2.Canny(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 80, 160)
    e[int(e.shape[0] * HEAD_KEEP):, :] = 0     # head-only lock -> body/clothing free
    return Image.fromarray(cv2.cvtColor(e, cv2.COLOR_GRAY2RGB)).resize((SIZE, SIZE))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--count", type=int, default=None)
    ap.add_argument("--offload", action="store_true", help="for <40GB GPUs (RTX 4090)")
    a = ap.parse_args()
    toks = json.loads(DNA.read_text(encoding="utf-8"))
    end = len(toks) if a.count is None else a.start + a.count
    toks = [t for t in toks if a.start <= t["token_id"] < end]
    OUT.mkdir(parents=True, exist_ok=True)
    pipe = build_pipe(a.offload); ctrl = canny()
    print(f"Rendering {len(toks)} (control={CONTROL_SCALE}, lora={LORA_SCALE}, steps={STEPS}, "
          f"head_keep={HEAD_KEEP}) + de-grain + crop")
    done = skip = 0
    for t in toks:
        out = OUT / f"{t['token_id']}.png"
        if out.exists() and out.stat().st_size > 0:
            skip += 1; continue
        g = torch.Generator("cuda").manual_seed(int(t["seed"]) % (2**31))
        img = pipe(prompt=t["prompt"], control_image=ctrl,
                   controlnet_conditioning_scale=CONTROL_SCALE, num_inference_steps=STEPS,
                   guidance_scale=GUIDANCE, height=SIZE, width=SIZE, generator=g,
                   joint_attention_kwargs={"scale": LORA_SCALE}).images[0]
        finalize(img).save(out)
        done += 1
        if done % 25 == 0:
            print(f"  {done} rendered, {skip} skipped")
    print(f"[OK] rendered={done} skipped={skip} -> {OUT}")


if __name__ == "__main__":
    main()
