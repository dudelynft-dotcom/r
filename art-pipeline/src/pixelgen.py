"""
ROBARK pixel art generator — layered, deterministic, NO AI.

Draws a base pixel dog (front-facing bust) + weighted pixel trait layers on a
32x32 grid, then upscales with hard NEAREST edges for crisp CryptoPunk-style
pixels. Same base dog every time → perfect consistency. Each token is a unique
weighted trait combo with metadata + rarity.

    python -m src.pixelgen --count 10          # sample sheet
    python -m src.pixelgen --size 10000        # full collection
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output" / "pixelgen"
G = 32          # grid
SCALE = 30      # px per cell -> 960x960
OUTLINE = (26, 22, 18)

# ── palettes ──────────────────────────────────────────────────────────────────
BG = {
    "Sky Blue": (150, 205, 215), "Bubblegum": (240, 200, 210),
    "Mint": (170, 225, 190), "Butter": (240, 225, 160),
    "Lilac": (205, 195, 235), "Slate": (120, 130, 150),
}
FUR = {
    "Cream": ((236, 200, 150), (210, 170, 115)),
    "Golden": ((232, 165, 75), (195, 130, 50)),
    "Grey": ((155, 158, 168), (120, 123, 135)),
    "Chocolate": ((150, 100, 60), (115, 75, 45)),
    "Zombie": ((125, 180, 95), (95, 145, 70)),
    "Ghost": ((238, 238, 232), (205, 205, 200)),
}
SUIT = {
    "Black Suit": (34, 34, 40), "Navy Puffer": (40, 52, 84),
    "Red Track": (175, 55, 55), "Grey Hoodie": (95, 100, 112),
    "Denim": (70, 110, 150),
}
GLASSES = {
    "None": None, "Purple Frames": (150, 60, 200), "Shades": (24, 24, 28),
    "3D Glasses": "3d", "VR Visor": (30, 30, 36), "Nerd": (60, 60, 70),
}
HAT = {
    "None": None, "Red Cap": (180, 55, 55), "Beanie": (60, 110, 170),
    "Crown": (235, 195, 70), "Halo": (240, 220, 120),
}
MOUTH = {
    "Cigarette": "cig", "Cigar": "cigar", "Pipe": "pipe", "Tongue": "tongue", "None": None,
}

WEIGHTS = {
    "Background": {k: w for k, w in zip(BG, [26, 18, 16, 14, 14, 12])},
    "Fur": {k: w for k, w in zip(FUR, [34, 22, 16, 14, 8, 6])},
    "Suit": {k: w for k, w in zip(SUIT, [30, 22, 20, 16, 12])},
    "Glasses": {k: w for k, w in zip(GLASSES, [26, 22, 20, 16, 8, 8])},
    "Hat": {k: w for k, w in zip(HAT, [44, 18, 16, 12, 10])},
    "Mouth": {k: w for k, w in zip(MOUTH, [34, 16, 12, 14, 24])},
}


def pick(rng, layer):
    opts = WEIGHTS[layer]
    total = sum(opts.values())
    r = rng.uniform(0, total)
    up = 0
    for k, w in opts.items():
        up += w
        if r <= up:
            return k
    return list(opts)[-1]


# ── drawing ───────────────────────────────────────────────────────────────────
def draw_dog(traits) -> Image.Image:
    im = Image.new("RGB", (G, G), BG[traits["Background"]])
    d = ImageDraw.Draw(im)
    fur, furD = FUR[traits["Fur"]]
    muzz = tuple(min(255, c + 22) for c in fur)

    # shoulders / outfit
    d.rectangle([6, 25, 25, 31], fill=SUIT[traits["Suit"]], outline=OUTLINE)
    d.rectangle([14, 25, 17, 28], fill=(245, 245, 245))  # collar/shirt

    # ears (behind head), droopy on the sides
    d.ellipse([5, 9, 11, 22], fill=furD, outline=OUTLINE)
    d.ellipse([20, 9, 26, 22], fill=furD, outline=OUTLINE)
    # head
    d.ellipse([8, 6, 23, 24], fill=fur, outline=OUTLINE)
    # muzzle
    d.ellipse([11, 16, 20, 24], fill=muzz, outline=OUTLINE)

    # eyes (unless visor covers them)
    if traits["Glasses"] != "VR Visor":
        for ex in (12, 17):
            d.rectangle([ex, 13, ex + 2, 15], fill=(255, 255, 255), outline=OUTLINE)
            d.point((ex + 1, 14), fill=(20, 18, 16))

    # nose
    d.ellipse([14, 17, 17, 20], fill=(22, 18, 14))

    _draw_mouth(d, traits["Mouth"])
    _draw_glasses(d, traits["Glasses"])
    _draw_hat(d, traits["Hat"])
    return im


def _draw_glasses(d, g):
    if g == "None" or g is None:
        return
    if g == "3d":
        d.rectangle([11, 12, 15, 16], fill=(200, 50, 50), outline=OUTLINE)
        d.rectangle([16, 12, 20, 16], fill=(50, 90, 200), outline=OUTLINE)
        return
    col = GLASSES[g]
    if g == "VR Visor":
        d.rectangle([9, 11, 22, 17], fill=col, outline=OUTLINE)
        d.rectangle([11, 13, 20, 15], fill=(80, 160, 220))
        return
    # framed lenses
    d.rectangle([11, 12, 15, 16], fill=None, outline=col, width=1)
    d.rectangle([16, 12, 20, 16], fill=None, outline=col, width=1)
    d.line([15, 13, 16, 13], fill=col)
    if g in ("Shades",):
        d.rectangle([11, 12, 15, 16], fill=col)
        d.rectangle([16, 12, 20, 16], fill=col)


def _draw_hat(d, h):
    if h == "None" or h is None:
        return
    col = HAT[h]
    if h == "Halo":
        d.ellipse([11, 2, 20, 5], fill=None, outline=col, width=1)
    elif h == "Crown":
        d.rectangle([10, 4, 21, 7], fill=col, outline=OUTLINE)
        for x in (10, 15, 21):
            d.point((x, 3), fill=col)
    elif h == "Beanie":
        d.rectangle([8, 4, 23, 8], fill=col, outline=OUTLINE)
        d.rectangle([8, 8, 23, 9], fill=tuple(max(0, c - 30) for c in col))
    else:  # cap
        d.rectangle([9, 5, 22, 8], fill=col, outline=OUTLINE)
        d.rectangle([20, 7, 26, 9], fill=col, outline=OUTLINE)  # brim


def _draw_mouth(d, m):
    if m == "None" or m is None:
        return
    if m == "Tongue":
        d.rectangle([15, 20, 17, 22], fill=(210, 90, 110), outline=OUTLINE)
        return
    # smoking items: stick from mouth to the left + smoke + ember
    y = 21
    if m == "cig":
        d.rectangle([7, y, 14, y + 1], fill=(245, 245, 240), outline=None)
        d.point((7, y), fill=(220, 70, 50))           # ember
    elif m == "cigar":
        d.rectangle([6, y, 14, y + 1], fill=(120, 80, 45))
        d.point((6, y), fill=(230, 120, 40))
    elif m == "pipe":
        d.rectangle([8, y, 13, y + 1], fill=(90, 60, 40))
        d.rectangle([6, y + 1, 8, y + 3], fill=(90, 60, 40))
    # smoke
    for i, sy in enumerate(range(y - 1, y - 5, -1)):
        d.point((6 - (i % 2), sy), fill=(225, 230, 235))


# ── collection ────────────────────────────────────────────────────────────────
def dna(traits):
    raw = "|".join(f"{k}={v}" for k, v in sorted(traits.items()))
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def render(traits) -> Image.Image:
    return draw_dog(traits).resize((G * SCALE, G * SCALE), Image.NEAREST)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=10)
    ap.add_argument("--size", type=int, default=None)
    ap.add_argument("--seed", type=int, default=6969)
    args = ap.parse_args()
    n = args.size or args.count
    OUT.mkdir(parents=True, exist_ok=True)

    rng = random.Random(args.seed)
    seen, made = set(), []
    while len(made) < n and len(seen) < n * 50:
        traits = {layer: pick(rng, layer) for layer in WEIGHTS}
        h = dna(traits)
        if h in seen:
            continue
        seen.add(h)
        tid = len(made)
        render(traits).save(OUT / f"{tid}.png")
        made.append({"token_id": tid, "dna": h, "traits": traits})

    (OUT / "_dna.json").write_text(json.dumps(made, indent=2), encoding="utf-8")
    print(f"[OK] {len(made)} pixel ROBARK -> {OUT}")


if __name__ == "__main__":
    main()
