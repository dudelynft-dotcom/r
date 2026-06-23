"""Broadcast Army generator: composites layered traits into unique pixel-punks.

Modes:
  --match            render the single reference-matching punk
  --variants         render the 6 curated style variants
  --preview N        render a sheet of N random punks
  --collection 10000 mint a full 10K collection with rarity ranking
"""
from __future__ import annotations
import argparse
import json
import random
import time
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).parent
CONFIG_PATH = ROOT / "config.json"
TRAITS = ROOT / "traits"
OUT = ROOT / "output"

_SPRITE_CACHE: dict[tuple[str, str], Image.Image] = {}

# 4-color "TLB Mono" palette — Black, Silver, White, Red.
MONO_PALETTE = [
    (25, 25, 28),      # BLACK
    (160, 168, 180),   # SILVER
    (220, 224, 232),   # WHITE
    (170, 45, 40),     # RED
]


def quantize_to_palette(img: Image.Image, palette_colors) -> Image.Image:
    """Map each opaque pixel to the nearest color in the palette."""
    import numpy as np
    arr = np.array(img)
    rgb = arr[..., :3].astype(np.int32)
    alpha = arr[..., 3]
    pal = np.array(palette_colors, dtype=np.int32)
    diff = rgb[:, :, None, :] - pal[None, None, :, :]
    dist2 = (diff ** 2).sum(axis=-1)
    nearest = dist2.argmin(axis=-1)
    out_rgb = pal[nearest]
    out = np.zeros_like(arr)
    out[..., :3] = out_rgb
    out[..., 3] = alpha
    return Image.fromarray(out, "RGBA")


def _force_picks(layers, rng, forced):
    """Pick traits, but force any layer named in `forced` to that file."""
    picks = []
    for layer in layers:
        if layer["name"] in forced:
            wanted = forced[layer["name"]]
            picks.append(next(o for o in layer["options"] if o["file"] == wanted))
        else:
            picks.append(weighted_pick(rng, layer["options"]))
    return picks


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_sprite(folder: str, file_name: str) -> Image.Image:
    key = (folder, file_name)
    if key not in _SPRITE_CACHE:
        _SPRITE_CACHE[key] = Image.open(TRAITS / folder / file_name).convert("RGBA")
    return _SPRITE_CACHE[key]


def warm_cache(layers):
    for layer in layers:
        for opt in layer["options"]:
            load_sprite(layer["folder"], opt["file"])


def weighted_pick(rng: random.Random, options):
    weights = [o["weight"] for o in options]
    return rng.choices(options, weights=weights, k=1)[0]


def compose(layers, picks) -> Image.Image:
    base = None
    for layer, pick in zip(layers, picks):
        img = load_sprite(layer["folder"], pick["file"])
        if base is None:
            base = img.copy()
        else:
            base = Image.alpha_composite(base, img)
    return base


def upscale(img: Image.Image, factor: int) -> Image.Image:
    if factor <= 1:
        return img
    w, h = img.size
    return img.resize((w * factor, h * factor), Image.NEAREST)


def signature_key(picks) -> tuple:
    return tuple(p["file"] for p in picks)


def _canvas_size(layers):
    sample_path = TRAITS / layers[0]["folder"] / layers[0]["options"][0]["file"]
    with Image.open(sample_path) as im:
        return im.size


# ============================================================
#  10K COLLECTION with rarity ranking
# ============================================================
def generate_collection(size: int, scale: int, seed: int):
    cfg = load_config()
    rng = random.Random(seed)
    layers = cfg["layers"]

    images_dir = OUT / "images"
    meta_dir = OUT / "metadata"
    images_dir.mkdir(parents=True, exist_ok=True)
    meta_dir.mkdir(parents=True, exist_ok=True)

    print(f"[1/4] Loading sprites...")
    warm_cache(layers)

    print(f"[2/4] Generating {size} unique trait combinations...")
    seen = set()
    minted = []
    attempts = 0
    max_attempts = size * 30
    while len(minted) < size and attempts < max_attempts:
        attempts += 1
        picks = [weighted_pick(rng, layer["options"]) for layer in layers]
        key = signature_key(picks)
        if key in seen:
            continue
        seen.add(key)
        minted.append(picks)

    if len(minted) < size:
        print(f"  WARN: only {len(minted)} unique combos available")

    # Trait counts (for rarity)
    trait_counts: dict[tuple[str, str], int] = {}
    for picks in minted:
        for layer, pick in zip(layers, picks):
            tk = (layer["name"], pick["name"])
            trait_counts[tk] = trait_counts.get(tk, 0) + 1

    print(f"[3/4] Computing rarity scores...")
    scores = []
    for i, picks in enumerate(minted):
        score = sum(1.0 / trait_counts[(layer["name"], pick["name"])]
                    for layer, pick in zip(layers, picks))
        scores.append(score)

    # Rank (highest score = #1 rarest)
    order = sorted(range(len(minted)), key=lambda i: -scores[i])
    ranks = {i: rank + 1 for rank, i in enumerate(order)}

    print(f"[4/4] Rendering {len(minted)} images at scale={scale}x...")
    t0 = time.time()
    for i, picks in enumerate(minted):
        token_id = i + 1
        img = compose(layers, picks)
        if scale > 1:
            img = upscale(img, scale)
        img.save(images_dir / f"{token_id:05d}.png")

        meta = {
            "name": f"{cfg['name']} #{token_id:05d}",
            "description": cfg["description"],
            "image": f"{token_id:05d}.png",
            "rarity_rank": ranks[i],
            "rarity_score": round(scores[i], 4),
            "attributes": [
                {"trait_type": layer["name"], "value": pick["name"]}
                for layer, pick in zip(layers, picks)
            ],
        }
        with open(meta_dir / f"{token_id:05d}.json", "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        if (i + 1) % 500 == 0:
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed
            eta = (len(minted) - i - 1) / rate
            print(f"  {i + 1}/{len(minted)} ({rate:.0f}/s, ETA {eta:.0f}s)")

    # Trait frequency report
    freq_report = {}
    for layer in layers:
        layer_name = layer["name"]
        freq_report[layer_name] = {}
        for opt in layer["options"]:
            count = trait_counts.get((layer_name, opt["name"]), 0)
            freq_report[layer_name][opt["name"]] = {
                "count": count,
                "percent": round(count / len(minted) * 100, 2),
            }
    with open(OUT / "trait_frequencies.json", "w", encoding="utf-8") as f:
        json.dump(freq_report, f, indent=2)

    # Top 25 rarest preview sheet
    _render_top_rare_sheet(layers, minted, scores, scale=15, top_n=25, cols=5)

    print(f"\nDONE. {len(minted)} unique punks minted.")
    print(f"  images:   {images_dir}")
    print(f"  metadata: {meta_dir}")
    print(f"  rarity:   {OUT / 'trait_frequencies.json'}")
    print(f"  preview:  {OUT / 'top_rare.png'}")


def _render_top_rare_sheet(layers, minted, scores, scale: int, top_n: int, cols: int):
    canvas_w, canvas_h = _canvas_size(layers)
    cell_w = canvas_w * scale
    cell_h = canvas_h * scale
    rows = (top_n + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * cell_w, rows * cell_h), (15, 15, 20, 255))

    order = sorted(range(len(minted)), key=lambda i: -scores[i])[:top_n]
    for slot, idx in enumerate(order):
        img = compose(layers, minted[idx])
        img = upscale(img, scale)
        x = (slot % cols) * cell_w
        y = (slot // cols) * cell_h
        sheet.paste(img, (x, y), img)
    sheet.save(OUT / "top_rare.png")


# ============================================================
#  PREVIEW / VARIANTS / MATCH (existing helpers)
# ============================================================
def generate_preview(count: int, scale: int, seed: int, cols: int = 4):
    cfg = load_config()
    rng = random.Random(seed)
    layers = cfg["layers"]
    canvas_w, canvas_h = _canvas_size(layers)
    warm_cache(layers)

    rows = (count + cols - 1) // cols
    cell_w, cell_h = canvas_w * scale, canvas_h * scale
    sheet = Image.new("RGBA", (cols * cell_w, rows * cell_h), (15, 15, 20, 255))

    seen = set()
    placed = 0
    attempts = 0
    while placed < count and attempts < count * 50:
        attempts += 1
        picks = [weighted_pick(rng, layer["options"]) for layer in layers]
        key = signature_key(picks)
        if key in seen:
            continue
        seen.add(key)
        img = compose(layers, picks)
        img = upscale(img, scale)
        x = (placed % cols) * cell_w
        y = (placed // cols) * cell_h
        sheet.paste(img, (x, y), img)
        placed += 1

    OUT.mkdir(exist_ok=True)
    out_path = OUT / "preview.png"
    sheet.save(out_path)
    print(f"Preview ({placed} punks, {cols}x{rows}) -> {out_path}")
    return out_path


# Curated style variants (kept for reference)
VARIANTS = [
    {
        "title": "Classic Zombie",
        "Background": "sky.png", "Type": "zombie.png",
        "Outfit": "broadcaster_jacket.png", "Hair": "long_black.png",
        "Eyes": "shades_purple.png", "Mouth": "cigarette.png",
        "Accessory": "none.png",
    },
    {
        "title": "Cowboy Anchor",
        "Background": "signal.png", "Type": "pale.png",
        "Outfit": "suit_anchor.png", "Hair": "cowboy_hat.png",
        "Eyes": "aviators.png", "Mouth": "cigar.png",
        "Accessory": "neck_chain.png",
    },
    {
        "title": "Beanie Outlaw",
        "Background": "crt.png", "Type": "robot.png",
        "Outfit": "hoodie_grey.png", "Hair": "beanie.png",
        "Eyes": "eyepatch.png", "Mouth": "broadcast_mic.png",
        "Accessory": "headphones.png",
    },
    {
        "title": "Afro Cyclops",
        "Background": "broadcast.png", "Type": "zombie.png",
        "Outfit": "static_tee.png", "Hair": "frizzy_afro.png",
        "Eyes": "cyclops_visor.png", "Mouth": "medical_mask.png",
        "Accessory": "face_tattoo.png",
    },
]


def _picks_from_variant(layers, variant):
    picks = []
    for layer in layers:
        wanted = variant.get(layer["name"])
        match = next((o for o in layer["options"] if o["file"] == wanted), layer["options"][0])
        picks.append(match)
    return picks


def generate_variants(scale: int, cols: int = 2):
    cfg = load_config()
    layers = cfg["layers"]
    canvas_w, canvas_h = _canvas_size(layers)
    cell_w, cell_h = canvas_w * scale, canvas_h * scale
    warm_cache(layers)

    OUT.mkdir(exist_ok=True)
    variants_dir = OUT / "variants"
    variants_dir.mkdir(parents=True, exist_ok=True)

    n = len(VARIANTS)
    rows = (n + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * cell_w, rows * cell_h), (15, 15, 20, 255))

    for i, variant in enumerate(VARIANTS):
        picks = _picks_from_variant(layers, variant)
        img = compose(layers, picks)
        img = upscale(img, scale)
        slug = variant["title"].lower().replace(" ", "_")
        img.save(variants_dir / f"{i + 1:02d}_{slug}.png")
        x = (i % cols) * cell_w
        y = (i // cols) * cell_h
        sheet.paste(img, (x, y), img)

    sheet_path = OUT / "variants.png"
    sheet.save(sheet_path)
    print(f"Wrote {n} variants -> {variants_dir}, sheet -> {sheet_path}")
    return sheet_path


SLONKS_BG = (28, 33, 46, 255)  # OpenSea card navy
SLONKS_CROP_TOP, SLONKS_CROP_BOTTOM = 0, 24


def generate_slonks_collection(size: int, scale: int, seed: int):
    """Mint a 10K face-only Slonks-style collection on uniform dark bg."""
    cfg = load_config()
    rng = random.Random(seed)
    layers = cfg["layers"]
    canvas_w, _ = _canvas_size(layers)
    warm_cache(layers)

    non_bg_layers = [l for l in layers if l["name"] != "Background"]
    crop_h = SLONKS_CROP_BOTTOM - SLONKS_CROP_TOP

    out_root = OUT / "slonks"
    images_dir = out_root / "images"
    meta_dir = out_root / "metadata"
    images_dir.mkdir(parents=True, exist_ok=True)
    meta_dir.mkdir(parents=True, exist_ok=True)

    print(f"[1/4] Generating {size} unique trait combos (face-only edition)...")
    seen = set()
    minted = []
    attempts = 0
    while len(minted) < size and attempts < size * 30:
        attempts += 1
        picks = [weighted_pick(rng, l["options"]) for l in layers]
        # Background is ignored for image, but keep it in metadata for trait variety
        key = signature_key(picks)
        if key in seen:
            continue
        seen.add(key)
        minted.append(picks)
    if len(minted) < size:
        print(f"  WARN: only {len(minted)} unique combos available")

    # Trait counts (no background — uniform bg)
    trait_counts = {}
    for picks in minted:
        for layer, pick in zip(layers, picks):
            if layer["name"] == "Background":
                continue
            tk = (layer["name"], pick["name"])
            trait_counts[tk] = trait_counts.get(tk, 0) + 1

    print(f"[2/4] Computing rarity scores...")
    scores = []
    for picks in minted:
        s = 0.0
        for layer, pick in zip(layers, picks):
            if layer["name"] == "Background":
                continue
            s += 1.0 / trait_counts[(layer["name"], pick["name"])]
        scores.append(s)
    order = sorted(range(len(minted)), key=lambda i: -scores[i])
    ranks = {i: rank + 1 for rank, i in enumerate(order)}

    print(f"[3/4] Rendering face-only at scale={scale}x on dark navy bg...")
    t0 = time.time()
    for i, picks in enumerate(minted):
        token_id = i + 1
        non_bg_picks = [p for l, p in zip(layers, picks) if l["name"] != "Background"]
        body = compose(non_bg_layers, non_bg_picks)
        face = body.crop((0, SLONKS_CROP_TOP, canvas_w, SLONKS_CROP_BOTTOM))
        cell = Image.new("RGBA", (canvas_w, crop_h), SLONKS_BG)
        cell = Image.alpha_composite(cell, face)
        if scale > 1:
            cell = upscale(cell, scale)
        cell.save(images_dir / f"{token_id:05d}.png")

        meta = {
            "name": f"{cfg['name']} #{token_id:05d}",
            "description": cfg["description"],
            "image": f"{token_id:05d}.png",
            "rarity_rank": ranks[i],
            "rarity_score": round(scores[i], 4),
            "edition": "Slonks-style 24x24",
            "attributes": [
                {"trait_type": layer["name"], "value": pick["name"]}
                for layer, pick in zip(layers, picks)
                if layer["name"] != "Background"
            ],
        }
        with open(meta_dir / f"{token_id:05d}.json", "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        if (i + 1) % 500 == 0:
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed
            eta = (len(minted) - i - 1) / rate
            print(f"  {i + 1}/{len(minted)} ({rate:.0f}/s, ETA {eta:.0f}s)")

    print(f"[4/4] Trait frequency report + top-rare sheet...")
    freq_report = {}
    for layer in layers:
        if layer["name"] == "Background":
            continue
        freq_report[layer["name"]] = {
            opt["name"]: {
                "count": trait_counts.get((layer["name"], opt["name"]), 0),
                "percent": round(trait_counts.get((layer["name"], opt["name"]), 0) / len(minted) * 100, 2),
            }
            for opt in layer["options"]
        }
    with open(out_root / "trait_frequencies.json", "w", encoding="utf-8") as f:
        json.dump(freq_report, f, indent=2)

    # Top-25 rarest sheet
    canvas_w_, crop_h_ = canvas_w, crop_h
    sheet_scale = 12
    sheet_cell_w = canvas_w_ * sheet_scale
    sheet_cell_h = crop_h_ * sheet_scale
    cols_n = 5
    rows_n = 5
    sheet = Image.new("RGBA", (cols_n * sheet_cell_w, rows_n * sheet_cell_h), SLONKS_BG)
    top_idx = order[:25]
    for slot, idx in enumerate(top_idx):
        token_id = idx + 1
        with Image.open(images_dir / f"{token_id:05d}.png") as src:
            img = src.convert("RGBA").resize((sheet_cell_w, sheet_cell_h), Image.NEAREST)
        x = (slot % cols_n) * sheet_cell_w
        y = (slot // cols_n) * sheet_cell_h
        sheet.paste(img, (x, y), img)
    sheet.save(out_root / "top_rare.png")

    print(f"\nDONE. {len(minted)} Slonks-style punks minted.")
    print(f"  images:   {images_dir}")
    print(f"  metadata: {meta_dir}")
    print(f"  preview:  {out_root / 'top_rare.png'}")


def generate_slonks_style(count: int, scale: int, seed: int, cols: int = 6) -> Path:
    """Slonks-style render: face-only crop, uniform dark background."""
    cfg = load_config()
    rng = random.Random(seed)
    layers = cfg["layers"]
    canvas_w, canvas_h = _canvas_size(layers)
    warm_cache(layers)

    DARK_BG = (28, 33, 46, 255)  # OpenSea card navy
    CROP_TOP, CROP_BOTTOM = 0, 24  # square face-only

    non_bg_layers = [l for l in layers if l["name"] != "Background"]
    crop_w, crop_h = canvas_w, CROP_BOTTOM - CROP_TOP
    cell_w, cell_h = crop_w * scale, crop_h * scale
    rows_n = (count + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * cell_w, rows_n * cell_h), DARK_BG)

    seen = set()
    placed = 0
    attempts = 0
    while placed < count and attempts < count * 50:
        attempts += 1
        picks_all = [weighted_pick(rng, l["options"]) for l in layers]
        key = signature_key(picks_all)
        if key in seen:
            continue
        seen.add(key)
        picks_no_bg = [p for l, p in zip(layers, picks_all) if l["name"] != "Background"]
        body = compose(non_bg_layers, picks_no_bg)
        face = body.crop((0, CROP_TOP, canvas_w, CROP_BOTTOM))
        cell = Image.new("RGBA", (crop_w, crop_h), DARK_BG)
        cell = Image.alpha_composite(cell, face)
        cell = upscale(cell, scale)
        x = (placed % cols) * cell_w
        y = (placed // cols) * cell_h
        sheet.paste(cell, (x, y), cell)
        placed += 1

    OUT.mkdir(exist_ok=True)
    out = OUT / "slonks_style.png"
    sheet.save(out)
    print(f"Slonks-style ({placed} punks) -> {out}")
    return out


def generate_hero_grid(count: int = 100, cols: int = 10, cell_scale: int = 5,
                       mode: str = "first") -> Path:
    """Hero grid for marketing/landing page.
    mode='first': token IDs 1..N (random order from mint)
    mode='rare':  top N rarest by metadata rarity_rank
    """
    cfg = load_config()
    layers = cfg["layers"]
    canvas_w, canvas_h = _canvas_size(layers)
    cell_w = canvas_w * cell_scale
    cell_h = canvas_h * cell_scale
    rows = (count + cols - 1) // cols

    images_dir = OUT / "images"
    meta_dir = OUT / "metadata"

    if mode == "rare":
        ranked = []
        for path in sorted(meta_dir.glob("*.json")):
            with open(path, "r", encoding="utf-8") as f:
                m = json.load(f)
            ranked.append((m["rarity_rank"], int(path.stem)))
        ranked.sort()
        token_ids = [tid for _, tid in ranked[:count]]
    else:
        token_ids = list(range(1, count + 1))

    sheet = Image.new("RGBA", (cols * cell_w, rows * cell_h), (15, 15, 20, 255))
    for slot, token_id in enumerate(token_ids):
        path = images_dir / f"{token_id:05d}.png"
        if not path.exists():
            continue
        with Image.open(path) as src:
            img = src.convert("RGBA").resize((cell_w, cell_h), Image.NEAREST)
        x = (slot % cols) * cell_w
        y = (slot // cols) * cell_h
        sheet.paste(img, (x, y), img)

    out = OUT / f"hero_grid_{mode}.png"
    sheet.save(out)
    print(f"Hero grid {cols}x{rows} ({count} punks, mode={mode}) -> {out}")
    return out


def generate_match(scale: int):
    cfg = load_config()
    layers = cfg["layers"]
    target = {
        "Background": "sky.png", "Type": "zombie.png",
        "Outfit": "broadcaster_jacket.png", "Hair": "long_black.png",
        "Eyes": "shades_purple.png", "Mouth": "cigarette.png",
        "Accessory": "none.png",
    }
    warm_cache(layers)
    picks = _picks_from_variant(layers, target)
    img = compose(layers, picks)
    img = upscale(img, scale)
    OUT.mkdir(exist_ok=True)
    out = OUT / "match.png"
    img.save(out)
    print(f"Match -> {out}")
    return out


def main():
    ap = argparse.ArgumentParser(description="Broadcast Army generator")
    ap.add_argument("--preview", type=int, default=0, help="random preview sheet of N")
    ap.add_argument("--variants", action="store_true", help="curated 4-variant sheet")
    ap.add_argument("--match", action="store_true", help="single reference-match punk")
    ap.add_argument("--collection", type=int, default=0, help="mint full collection of N (Slonks-style)")
    ap.add_argument("--full-body", action="store_true", help="use legacy full-body 24x32 mint instead")
    ap.add_argument("--hero", type=int, default=0, help="hero grid of N from minted collection")
    ap.add_argument("--slonks", type=int, default=0, help="slonks-style face-only preview of N")
    ap.add_argument("--hero-mode", default="first", choices=["first", "rare"],
                    help="which N to pick for hero grid")
    ap.add_argument("--cols", type=int, default=4, help="grid columns for sheets")
    ap.add_argument("--scale", type=int, default=None, help="pixel scale factor")
    ap.add_argument("--seed", type=int, default=42, help="rng seed")
    args = ap.parse_args()

    cfg = load_config()
    scale = args.scale if args.scale is not None else cfg.get("scale", 25)

    if args.match:
        generate_match(scale)
    elif args.variants:
        generate_variants(scale, cols=args.cols if args.cols != 4 else 2)
    elif args.preview > 0:
        generate_preview(args.preview, scale, args.seed, args.cols)
    elif args.hero > 0:
        cols = args.cols if args.cols != 4 else 10
        generate_hero_grid(args.hero, cols=cols, mode=args.hero_mode)
    elif args.slonks > 0:
        cols = args.cols if args.cols != 4 else 6
        generate_slonks_style(args.slonks, scale, args.seed, cols=cols)
    elif args.collection > 0:
        if args.full_body:
            generate_collection(args.collection, scale, args.seed)
        else:
            generate_slonks_collection(args.collection, scale, args.seed)
    else:
        size = cfg.get("size", 10000)
        if args.full_body:
            generate_collection(size, scale, args.seed)
        else:
            generate_slonks_collection(size, scale, args.seed)


if __name__ == "__main__":
    main()
