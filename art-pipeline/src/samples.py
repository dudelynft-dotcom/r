"""
5 ROBARK samples: the SAME dog face + SAME OK-Guy style, deadpan thumbs-up pose,
different outfit + different fun background each. Backgrounds are varied themes
(not crypto), like the OK-Guy collection. Renders via fal.

    python -m src.samples
"""
from __future__ import annotations

from pathlib import Path

from .dna import Taxonomy
from .generate import fal, download, load_fal_key

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output" / "samples"

# The signature look kept constant so it's clearly the SAME character.
ICONIC = ("dark sunglasses pushed up resting on top of his head, "
          "a cigarette in his mouth with a small curl of smoke")

# no-text guard (OK-Guy keeps simple cel shading, so we do NOT forbid shading)
GUARD = ("absolutely no text, no words, no letters, no numbers, no signs, no "
         "logos, no watermark, no signature, no extra characters")

# (label, outfit, fun background) — varied themes in the art's style
SAMPLES = [
    ("1_paintdrip", "wearing a black suit and tie",
     "a bright blue sky with fluffy white clouds dripping like melting paint, colorful red, green and orange paint splatters dripping down, a melting green grassy ground"),
    ("2_storm", "wearing a blue denim jacket",
     "a dark purple stormy night sky crackling with glitchy yellow lightning bolts, heavy storm clouds, low green hills"),
    ("3_lasers", "wearing a navy puffer jacket",
     "a deep blue starry night sky with a crescent moon and stars, colorful red, green and blue laser beams crossing with bright spark bursts"),
    ("4_magic", "wearing a grey hoodie",
     "swirling blue and purple magic spirals with glowing floating crystals and glowing rune circles on the ground"),
    ("5_candy", "wearing a red tracksuit with white stripes",
     "a dreamy sky of cotton-candy pink and blue clouds with a rainbow, floating lollipops and candy"),
]


def main():
    key = load_fal_key()
    tax = Taxonomy.load()
    OUT.mkdir(parents=True, exist_ok=True)
    seed = 424200
    for name, outfit, bg in SAMPLES:
        prompt = ", ".join([tax.base_character, ICONIC, outfit, bg, tax.style, GUARD])
        out = OUT / f"robark_{name}.png"
        print(f"==> {name}")
        try:
            url = fal(prompt, seed, key)
            download(url, out)
            print(f"   [OK] {out.name}")
        except Exception as e:  # noqa: BLE001
            body = getattr(e, "read", lambda: b"")()
            print(f"   [X] {e} {body[:160] if body else ''}")
        seed += 7919
    print(f"\n[OK] samples -> {OUT}")


if __name__ == "__main__":
    main()
