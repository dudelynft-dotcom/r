"""
Generate the full ROBARK image per token (handmade style) via fal.ai.

This is the real art step: each token is rendered whole (character + traits +
background) from its prompt — no compositing, because traits change the body.

- fal samples: base FLUX dev validates the STYLE quickly/cheaply.
- full 10k on RunPod: run the SAME prompts through FLUX + a ROBARK character LoRA
  (see RUNPOD.md) so the dog stays perfectly on-model across the collection.

No-text + anti-AI is baked into every prompt; an optional OCR guard regenerates
any image that still shows text. Resumable (skips existing). Reads FAL_KEY from
env or web/.env.local.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parent
DNA = ROOT / "output" / "dna.json"
IMG_DIR = ROOT / "output" / "images"

MODEL = os.environ.get("FAL_MODEL", "fal-ai/flux/dev")


def load_fal_key() -> str:
    key = os.environ.get("FAL_KEY")
    if key:
        return key.strip()
    envf = REPO / "web" / ".env.local"
    for line in (envf.read_text(encoding="utf-8").splitlines() if envf.exists() else []):
        if line.strip().startswith("FAL_KEY="):
            return line.split("=", 1)[1].strip()
    sys.exit("FAL_KEY not found (env or web/.env.local)")


def make_text_detector():
    try:
        import pytesseract
        from PIL import Image
        pytesseract.get_tesseract_version()

        def has_text(p: Path) -> bool:
            txt = pytesseract.image_to_string(Image.open(p))
            return len([w for w in txt.split() if len(w) >= 3 and w.isalnum()]) >= 1
        return has_text
    except Exception:
        return None


def fal(prompt: str, seed: int, key: str) -> str:
    payload = {
        "prompt": prompt,
        "image_size": "square_hd",
        "num_images": 1,
        "num_inference_steps": 34,
        "guidance_scale": 3.6,  # crisper bold-outline adherence to the flat OK-Guy style
        "seed": seed,
        # OFF: the checker false-flags cartoon dogs and returns black images
        "enable_safety_checker": False,
    }
    req = urllib.request.Request(
        f"https://fal.run/{MODEL}",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Key {key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read())["images"][0]["url"]


def download(url: str, out: Path):
    out.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=120) as r:
        out.write_bytes(r.read())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--count", type=int, default=None)
    ap.add_argument("--text-retries", type=int, default=3)
    args = ap.parse_args()

    key = load_fal_key()
    toks = json.loads(DNA.read_text(encoding="utf-8"))
    end = len(toks) if args.count is None else args.start + args.count
    toks = [t for t in toks if args.start <= t["token_id"] < end]

    guard = make_text_detector()
    print(f"model={MODEL}  OCR text-guard: {'ON' if guard else 'OFF (prompt-only)'}")

    done = skip = fail = 0
    t0 = time.time()
    for t in toks:
        out = IMG_DIR / f"{t['token_id']}.png"
        if out.exists() and out.stat().st_size > 0:
            skip += 1
            continue
        ok = False
        for attempt in range(args.text_retries + 1):
            try:
                url = fal(t["prompt"], t["seed"] + attempt * 101, key)
                download(url, out)
            except Exception as e:  # noqa: BLE001
                body = getattr(e, "read", lambda: b"")()
                print(f"  [X] {t['token_id']}: {e} {body[:160] if body else ''}")
                break
            if guard and guard(out):
                print(f"  ~ {t['token_id']} had text, regen (try {attempt+1})")
                continue
            ok = True
            break
        done += ok
        fail += (not ok)
        if (done + skip) % 20 == 0:
            print(f"  {done} done, {skip} skipped, {fail} failed ({done/max(1e-9,time.time()-t0):.2f}/s)")

    print(f"\n[OK] done={done} skipped={skip} failed={fail} -> {IMG_DIR}")


if __name__ == "__main__":
    main()
