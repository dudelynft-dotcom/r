"""
PROOF: keep the FINAL structure, change only the traits.

Uses fal FLUX image-to-image with the FINAL piece as the init image, so the pose
/ composition / framing stay the same while the prompt swaps fur color, clothing,
headwear, eyewear, mouth item, hand item and background.

    python -m src.variants
"""
from __future__ import annotations

import base64
import json
import urllib.request
from pathlib import Path

from .generate import download, load_fal_key

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parent
FINAL = REPO / "art-previews" / "FINAL" / "08_degen_trenches.png"
OUT = ROOT / "output" / "variants"

ENDPOINT = "fal-ai/flux/dev/image-to-image"

# Describe the WHOLE target (same dog + pose) with the swapped elements.
BASE = ("a hand-drawn cartoon dog in EXACTLY the same pose and composition, "
        "3/4 side view facing left, sleepy smug half-closed eyes, big black nose, "
        "a cigarette in his mouth with a curl of smoke, one paw raised holding "
        "{HAND} near his face, {FUR} fur, wearing {CLOTHES}, {NECK}, {HEAD} "
        "inside a comic panel border, {BG}, bold black outlines, flat colors, "
        "clean hand-drawn comic style, no text, no watermark")

VARIANTS = [
    ("v1_golden_beer", {
        "FUR": "golden", "CLOTHES": "a blue varsity letterman jacket",
        "NECK": "a gold chain", "HEAD": "no hat,", "HAND": "a can of beer",
        "BG": "a detailed dim bar background with neon glow"}),
    ("v2_grey_suit_phone", {
        "FUR": "grey", "CLOTHES": "a sharp black suit and tie",
        "NECK": "a diamond chain", "HEAD": "wearing dark sunglasses,",
        "HAND": "a smartphone showing a red chart", "BG": "a detailed office with red candle charts on a screen"}),
    ("v3_brown_hoodie_money", {
        "FUR": "brown", "CLOTHES": "a green hoodie",
        "NECK": "a gold chain", "HEAD": "wearing a red cap,",
        "HAND": "a fat stack of cash", "BG": "a detailed messy degen room with a glowing monitor"}),
]


def data_uri(p: Path) -> str:
    b64 = base64.b64encode(p.read_bytes()).decode()
    return f"data:image/png;base64,{b64}"


def img2img(image_uri: str, prompt: str, key: str, strength: float, seed: int) -> str:
    payload = {
        "image_url": image_uri,
        "prompt": prompt,
        "strength": strength,
        "num_inference_steps": 38,
        "guidance_scale": 3.5,
        "enable_safety_checker": False,
        "seed": seed,
    }
    req = urllib.request.Request(
        f"https://fal.run/{ENDPOINT}",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Key {key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read())["images"][0]["url"]


def main():
    key = load_fal_key()
    OUT.mkdir(parents=True, exist_ok=True)
    uri = data_uri(FINAL)
    # 0.72: enough to recolor/reclothe while holding the pose
    strength = 0.72
    seed = 313100
    for name, t in VARIANTS:
        prompt = BASE
        for k, v in t.items():
            prompt = prompt.replace("{" + k + "}", v)
        print(f"==> {name}")
        try:
            url = img2img(uri, prompt, key, strength, seed)
            download(url, OUT / f"{name}.png")
            print(f"   [OK] {name}.png")
        except Exception as e:  # noqa: BLE001
            body = getattr(e, "read", lambda: b"")()
            print(f"   [X] {e} {body[:200] if body else ''}")
        seed += 7919
    print(f"\n[OK] variants -> {OUT}")


if __name__ == "__main__":
    main()
