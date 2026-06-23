"""
ROBARK collection generator — SAME structure (the FINAL), different traits.

For each token: pick a unique weighted trait combo, build a prompt that keeps the
FINAL pose/composition and swaps the elements, render via fal img2img @0.85 with
the FINAL as the init image, (optional OCR no-text guard regenerates on text),
then write the image + OpenSea metadata + rarity.

    python -m src.collection --count 10        # sample batch
    python -m src.collection --size 10000      # full collection
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path

import yaml

import urllib.request

from .generate import download, load_fal_key, make_text_detector
from .variants import data_uri, FINAL

ROOT = Path(__file__).resolve().parent.parent
TRAITS = ROOT / "final_traits.yaml"
OUT = ROOT / "output" / "collection"
IMG = OUT / "images"
META = OUT / "metadata"

# Winning recipe: ControlNet-canny locks the FINAL structure + a flat-style LoRA
# makes it look genuinely hand-drawn (not AI-rendered).
ENDPOINT = "fal-ai/flux-lora-canny"
LORA_URL = ("https://huggingface.co/strangerzonehf/Flux-Sketch-Flat-LoRA/"
            "resolve/main/Sketch-Flat.safetensors")
LORA_SCALE = 1.05


def render(control_uri: str, prompt: str, key: str, seed: int) -> str:
    payload = {
        "prompt": prompt,
        "image_url": control_uri,
        "loras": [{"path": LORA_URL, "scale": LORA_SCALE}],
        "num_inference_steps": 30,
        "guidance_scale": 3.5,
        "num_images": 1,
        "enable_safety_checker": False,
        "seed": seed,
    }
    req = urllib.request.Request(
        f"https://fal.run/{ENDPOINT}",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Key {key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=240) as r:
        return json.loads(r.read())["images"][0]["url"]

BASE = (
    "a hand-drawn cartoon dog, the EXACT same pose and composition as the "
    "reference image, 3/4 side view facing left, sleepy smug half-closed eyes, "
    "big black nose, {Mouth}, one paw raised holding {Hand} near his face, "
    "{Fur}, wearing {Clothing}, {constant}, {Headwear}, {Eyewear} inside a comic "
    "panel border, {Background}, bold black outlines, flat colors, clean "
    "hand-drawn comic style, absolutely no text, no words, no letters, no "
    "numbers, no signs, no logos, no watermark, no signature"
)


def load_tax():
    d = yaml.safe_load(TRAITS.read_text(encoding="utf-8"))
    return d["collection"], d["layers"]


def pick(rng, options):
    total = sum(o["weight"] for o in options)
    r = rng.uniform(0, total)
    up = 0.0
    for o in options:
        up += o["weight"]
        if r <= up:
            return o
    return options[-1]


def build_prompt(coll, layers, chosen):
    frag = {}
    for L in layers:
        opt = next(o for o in L["weights"] if o["value"] == chosen[L["name"]])
        frag[L["name"]] = (opt.get("prompt") or "").strip()
    p = BASE
    p = p.replace("{constant}", coll.get("constant", ""))
    for L in layers:
        name = L["name"]
        val = frag[name]
        if name == "Eyewear":
            val = (val + ",") if val else ""        # optional
        if name == "Headwear" and not val:
            val = "no hat"
        p = p.replace("{" + name + "}", val)
    return ("Sketch Flat: " + p +
            ", completely flat solid colors, no shading, no gradients, bold black "
            "outlines, minimal hand-drawn indie comic, drawn by a human not AI")


def dna(chosen):
    raw = "|".join(f"{k}={v}" for k, v in sorted(chosen.items()))
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def rarity(tokens):
    n = len(tokens)
    counts = {}
    for t in tokens:
        for k, v in t["traits"].items():
            counts[(k, v)] = counts.get((k, v), 0) + 1
    for t in tokens:
        t["rarity_score"] = round(sum(n / counts[(k, v)] for k, v in t["traits"].items()), 3)
    for rank, t in enumerate(sorted(tokens, key=lambda x: -x["rarity_score"]), 1):
        t["rank"] = rank


def tier(rank, total):
    p = rank / total
    return ("Mythic" if p <= .005 else "Legendary" if p <= .05 else
            "Epic" if p <= .15 else "Rare" if p <= .4 else "Common")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=10)
    ap.add_argument("--size", type=int, default=None)
    ap.add_argument("--seed", type=int, default=6969)
    ap.add_argument("--image-cid", default="ipfs://REPLACE_WITH_IMAGE_FOLDER_CID")
    ap.add_argument("--text-retries", type=int, default=3)
    ap.add_argument("--dna-only", action="store_true",
                    help="only build dna.json + metadata (no rendering; for RunPod)")
    args = ap.parse_args()
    n = args.size or args.count

    coll, layers = load_tax()
    IMG.mkdir(parents=True, exist_ok=True)
    META.mkdir(parents=True, exist_ok=True)
    key = uri = guard = None
    if not args.dna_only:
        key = load_fal_key()
        uri = data_uri(FINAL)
        guard = make_text_detector()
        print(f"OCR no-text guard: {'ON' if guard else 'OFF (prompt-only)'}  "
              f"engine={ENDPOINT} + Sketch-Flat LoRA")

    rng = random.Random(args.seed)
    seen, tokens = set(), []
    while len(tokens) < n and len(seen) < n * 60:
        chosen = {L["name"]: pick(rng, L["weights"])["value"] for L in layers}
        h = dna(chosen)
        if h in seen:
            continue
        seen.add(h)
        tid = len(tokens)
        tokens.append({"token_id": tid, "dna": h, "traits": chosen,
                       "prompt": build_prompt(coll, layers, chosen),
                       "seed": args.seed + tid * 7919})

    rarity(tokens)

    # render (skipped in --dna-only mode)
    done = skip = fail = 0
    for t in (tokens if not args.dna_only else []):
        out = IMG / f"{t['token_id']}.png"
        if out.exists() and out.stat().st_size > 0:
            skip += 1
            continue
        ok = False
        for attempt in range(args.text_retries + 1):
            try:
                url = render(uri, t["prompt"], key, t["seed"] + attempt * 101)
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
        print(f"  [{'OK' if ok else 'X'}] #{t['token_id']}  "
              f"{t['traits']['Fur']}/{t['traits']['Clothing']}/{t['traits']['Hand']}")

    # metadata
    total = len(tokens)
    base = args.image_cid.rstrip("/")
    for t in tokens:
        attrs = [{"trait_type": k, "value": v} for k, v in t["traits"].items()]
        attrs.append({"trait_type": "Rarity Tier", "value": tier(t["rank"], total)})
        attrs.append({"trait_type": "Rarity Rank", "value": t["rank"], "display_type": "number"})
        (META / f"{t['token_id']}.json").write_text(json.dumps({
            "name": f"ROBARK #{t['token_id']}",
            "description": "ROBARK survived the crash. 10,000 hand-drawn degens, one iconic dog.",
            "image": f"{base}/{t['token_id']}.png",
            "attributes": attrs,
            "robark": {"dna": t["dna"], "seed": t["seed"], "rank": t["rank"], "rarity_score": t["rarity_score"]},
        }, indent=2), encoding="utf-8")
    (OUT / "_dna.json").write_text(json.dumps(tokens, indent=2), encoding="utf-8")

    print(f"\n[OK] rendered={done} skipped={skip} failed={fail}  -> {IMG}")


if __name__ == "__main__":
    main()
