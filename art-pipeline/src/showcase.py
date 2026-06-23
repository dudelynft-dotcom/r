"""
Curated showcase: 10 ROBARKs with 10 DIFFERENT trait sets and 10 DIFFERENT
detailed backgrounds, plus a few Legendary 1/1 "masterpieces". Hand-picked combos
(not random) so the reveal looks intentional. Renders via fal in the locked style.

    python -m src.showcase
"""
from __future__ import annotations

import json
from pathlib import Path

from .dna import Taxonomy, build_prompt, HARD_GUARD
from .generate import fal, download, load_fal_key

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output" / "showcase"

# 10 curated pieces: each a distinct background + distinct trait combo.
CURATED = [
    ("01_red_candle_city", {"Background": "Red Candle City", "Fur": "Classic Cream", "Eyes": "Tired Degen", "Mouth": "Cigarette", "Eyewear": "Shades on Forehead", "Headwear": "None", "Outfit": "Black Suit", "Chain": "Gold Chain", "Accessory": "None"}),
    ("02_liquidation_inferno", {"Background": "Liquidation Inferno", "Fur": "Black Lab", "Eyes": "Bloodshot", "Mouth": "Cigar", "Eyewear": "Shades On", "Headwear": "None", "Outfit": "Pinstripe Suit", "Chain": "Cuban Link", "Accessory": "Lighter"}),
    ("03_trading_meltdown", {"Background": "Trading Floor Meltdown", "Fur": "Ash Grey", "Eyes": "Cope Wide", "Mouth": "Vape Cloud", "Eyewear": "Nerd Glasses", "Headwear": "None", "Outfit": "Hoodie", "Chain": "Dog Tag", "Accessory": "Phone Red Chart"}),
    ("04_rug_pull_crater", {"Background": "Rug Pull Crater", "Fur": "Chocolate", "Eyes": "Dead Inside", "Mouth": "Cope Line", "Eyewear": "None", "Headwear": "None", "Outfit": "Hazmat Suit", "Chain": "None", "Accessory": "Trash Bag"}),
    ("05_casino_ruin", {"Background": "Casino Ruin", "Fur": "Golden", "Eyes": "Side Eye", "Mouth": "Toothpick", "Eyewear": "Monocle", "Headwear": "Crown", "Outfit": "Tuxedo", "Chain": "Diamond Chain", "Accessory": "None"}),
    ("06_eth_storm", {"Background": "ETH Storm", "Fur": "Blue Merle", "Eyes": "Laser Eyes", "Mouth": "Cigarette", "Eyewear": "Ski Goggles", "Headwear": "Beanie", "Outfit": "Puffer Jacket", "Chain": "Rope Chain", "Accessory": "None"}),
    ("07_bear_wasteland", {"Background": "Bear Wasteland", "Fur": "Patchy Mutt", "Eyes": "Side Eye", "Mouth": "Cope Line", "Eyewear": "Eye Patch", "Headwear": "Cowboy Hat", "Outfit": "Tank Top", "Chain": "None", "Accessory": "None"}),
    ("08_degen_trenches", {"Background": "Degen Trenches", "Fur": "Albino White", "Eyes": "Sleepy", "Mouth": "Blunt", "Eyewear": "None", "Headwear": "Durag", "Outfit": "Tracksuit", "Chain": "Gold Chain", "Accessory": "Coffee"}),
    ("09_vaporwave_dump", {"Background": "Vaporwave Dump", "Fur": "Zombie Green", "Eyes": "Hypno Spiral", "Mouth": "Bubblegum", "Eyewear": "Heart Glasses", "Headwear": "Party Hat", "Outfit": "Hawaiian Shirt", "Chain": "ETH Pendant", "Accessory": "Balloon"}),
    ("10_underwater_rekt", {"Background": "Underwater Rekt", "Fur": "Cream", "Eyes": "Teary", "Mouth": "Toothpick", "Eyewear": "Shades on Forehead", "Headwear": "Bucket Hat", "Outfit": "Hawaiian Shirt", "Chain": "Dog Tag", "Accessory": "Tiny Umbrella"}),
]

# Legendary 1/1 masterpieces — fully bespoke prompts in the locked style.
def legendary(tax: Taxonomy, scene: str) -> str:
    return ", ".join([tax.base_character, scene, tax.style, HARD_GUARD])

LEGENDARIES = [
    ("L1_golden_robark", "ROBARK as a solid gold statue dog, flat metallic gold fur, a flat gold suit, a gold crown, a thick gold cuban chain, glowing gold eyes, calm smug face, a detailed background of a swirling golden galaxy with falling gold coins"),
    ("L2_devil_robark", "ROBARK as a red devil dog, deep red fur, small black horns, glowing yellow eyes, a black suit, a cigar with thick smoke, sitting on a throne built of burning red candlestick bars, a detailed hellish background of flames and dark smoke"),
    ("L3_skeleton_robark", "ROBARK drawn as a cartoon skeleton dog, white bones showing through an open black suit, dark sunglasses, a cigarette, a gold chain, a detailed background of a foggy graveyard at night with crashing red charts in the sky"),
]


def main():
    key = load_fal_key()
    tax = Taxonomy.load()
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = []

    def render(name: str, prompt: str, seed: int):
        out = OUT / f"{name}.png"
        if out.exists() and out.stat().st_size > 0:
            print(f"  skip {name}")
            return
        print(f"==> {name}")
        try:
            url = fal(prompt, seed, key)
            download(url, out)
            manifest.append({"name": name, "prompt": prompt})
            print(f"   [OK] {out.name}")
        except Exception as e:  # noqa: BLE001
            body = getattr(e, "read", lambda: b"")()
            print(f"   [X] {e} {body[:160] if body else ''}")

    seed = 69690
    for name, traits in CURATED:
        render(name, build_prompt(tax, traits), seed)
        seed += 7919
    for name, scene in LEGENDARIES:
        render(name, legendary(tax, scene), seed)
        seed += 7919

    (OUT / "_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\n[OK] showcase -> {OUT}")


if __name__ == "__main__":
    main()
