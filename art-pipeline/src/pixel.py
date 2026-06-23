"""
Pixel-art ROBARK — CryptoPunks style, but the character is a DOG.

Generates a clean bust via fal, then snaps it to a real low-res pixel grid with
a limited palette (so it's crisp blocky pixels, not 'AI fake pixels'). Solid
pastel background, smoking + glasses traits like the reference punk.

    python -m src.pixel
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image

from .generate import fal, download, load_fal_key

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output" / "pixel"

BASE = (
    "pixel art avatar in the style of CryptoPunks, a cute dog character bust "
    "(head and shoulders only), blocky crisp pixels, low resolution 32x32 look, "
    "limited retro color palette, a dog face with droopy ears, a black dog nose "
    "and small pixel eyes, centered, flat solid {BG} background, retro 8-bit NFT "
    "profile picture"
)
GUARD = "no text, no words, no letters, no watermark, no signature, no border, no grid lines"

# (label, bg color word, traits) — same pixel style, dog, varied traits
PIECES = [
    ("1_classic", "light blue", "cream tan fur, purple square pixel glasses, smoking a cigarette with pixel smoke"),
    ("2_zombie", "pale blue", "zombie green fur, black 3d pixel glasses, smoking a cigarette with pixel smoke"),
    ("3_cap", "soft pink", "brown fur, a red pixel cap, dark pixel sunglasses, a small pixel pipe"),
    ("4_cool", "mint green", "grey fur, black VR pixel visor, a gold pixel chain, smoking a cigarette"),
    ("5_gold", "pale yellow", "golden fur, a tiny pixel crown, dark pixel sunglasses, smoking a cigar"),
]


def pixelate(src: Path, dst: Path, grid: int = 48, colors: int = 20, out: int = 960):
    im = Image.open(src).convert("RGB")
    # downscale to the pixel grid, clamp the palette, then hard-edge upscale
    small = im.resize((grid, grid), Image.BILINEAR)
    small = small.quantize(colors=colors, method=Image.Quantize.MAXCOVERAGE).convert("RGB")
    big = small.resize((out, out), Image.NEAREST)
    big.save(dst)


def main():
    key = load_fal_key()
    OUT.mkdir(parents=True, exist_ok=True)
    seed = 909001
    for name, bg, traits in PIECES:
        prompt = f"{BASE.replace('{BG}', bg)}, {traits}, {GUARD}"
        raw = OUT / f"raw_{name}.png"
        pix = OUT / f"robark_pixel_{name}.png"
        print(f"==> {name}")
        try:
            url = fal(prompt, seed, key)
            download(url, raw)
            pixelate(raw, pix)
            print(f"   [OK] {pix.name}")
        except Exception as e:  # noqa: BLE001
            body = getattr(e, "read", lambda: b"")()
            print(f"   [X] {e} {body[:160] if body else ''}")
        seed += 7919
    print(f"\n[OK] pixel samples -> {OUT}")


if __name__ == "__main__":
    main()
