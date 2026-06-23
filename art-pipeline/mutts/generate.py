"""
ROBARK pixel art — original engine (own code), distinct from BarkFi Mutts:
  • DROOPY floppy ears + rounder head (Mutts have pointy ears) -> own silhouette
  • CryptoPunk-style colour discipline: one harmonised master palette, muted
    backgrounds, flat fills, ~6-7 colours per image.
24x24 grid, trait overlays. Outputs PNG + SVG + metadata.

    python generate.py --preview 16
    python generate.py --collection 5555
"""
from __future__ import annotations
import argparse, json, random
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
GRID = 24

# ── ONE MASTER PALETTE (organised, minimal, harmonised) ───────────────────
INK = "#1b1714"          # single outline ink
CREAM = "#f5f0e2"        # eyes / teeth / highlights
ACCENT = "#c0492f"       # ROBARK rust-red (one brand accent)
ACCENT_L = "#e0917a"
GOLD = "#c79a44"         # only for "gold" rares

# Backgrounds — muted, low-saturation, harmonised (dog pops, like punks)
BGS = {"Bone": "#e6dfce", "Mist": "#d3d9d6", "Haze": "#ccd5dd",
       "Clay": "#e3d2c2", "Ash": "#cdccc6"}

# Fur family — each: (base, shadow, muzzle). Earth-tones + a few cool/special.
FURS = {
    "Sand":  ("#d0a868", "#a67e48", "#e3c690"),
    "Wheat": ("#e2cc99", "#b9a46f", "#f0e1bc"),
    "Stone": ("#a7a59b", "#7b796f", "#c5c3ba"),
    "Cocoa": ("#8b6043", "#5f3f2a", "#a67a58"),
    "Soot":  ("#332f2a", "#191310", "#4d4840"),
    "Chalk": ("#e5e0d2", "#bbb6a7", "#f3efe4"),
    "Moss":  ("#92a26d", "#6a794b", "#b0bc8d"),
    "Steel": ("#7e8fa9", "#596984", "#9eacc2"),
}
# Shirts — tight muted set
SHIRTS = {"None": None, "Rust": (ACCENT, "#8d2f1d"), "Navy": ("#36415d", "#222a40"),
          "Olive": ("#6f7a4c", "#4d5533"), "Stone": ("#7c7a70", "#56544c"),
          "Bone": ("#d6d0bf", "#a9a392")}


def rect(px, x1, y1, x2, y2, c):
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            px.append((x, y, c))


# ── Base portrait — droopy ears + rounded head (front-facing) ─────────────
def base_portrait(fur, shirt):
    B, D, M = fur
    O = INK
    px = []

    # Head (rounded, cols 6-17, rows 4-10)
    head = {4: (8, 15), 5: (7, 16), 6: (6, 17), 7: (6, 17), 8: (6, 17), 9: (7, 16), 10: (8, 15)}
    for y, (c0, c1) in head.items():
        rect(px, c0, y, c1, y, B)

    # Droopy ears (flaps framing the sides), drawn over head edges
    earL = {4: (6, 7), 5: (5, 7), 6: (4, 7), 7: (4, 6), 8: (4, 6), 9: (4, 6), 10: (4, 6), 11: (5, 6), 12: (5, 6)}
    for y, (c0, c1) in earL.items():
        rect(px, c0, y, c1, y, B)
        rect(px, 23 - c1, y, 23 - c0, y, B)          # mirror -> right ear
    # ear inner shadow
    for y in range(6, 11):
        px += [(6, y, D), (17, y, D)]
    # ear outer outline
    for x, y in [(6, 4), (5, 5), (4, 6), (4, 7), (4, 8), (4, 9), (4, 10), (5, 11), (5, 12), (6, 12)]:
        px.append((x, y, O)); px.append((23 - x, y, O))

    # Head outline (rounded perimeter, open at bottom-centre for the snout)
    for x in range(8, 16): px.append((x, 4, O))
    for x, y in [(7, 5), (16, 5), (6, 6), (17, 6), (6, 7), (17, 7), (6, 8), (17, 8), (7, 9), (16, 9)]:
        px.append((x, y, O))
    for x in (8, 9, 14, 15): px.append((x, 10, O))

    # Snout (centred, muzzle tone), rows 11-14
    snout = {11: (9, 14), 12: (9, 14), 13: (10, 13), 14: (10, 13)}
    for y, (c0, c1) in snout.items():
        rect(px, c0, y, c1, y, M)
    for x, y in [(8, 11), (15, 11), (8, 12), (15, 12), (9, 13), (14, 13), (9, 14), (14, 14)]:
        px.append((x, y, O))
    rect(px, 10, 15, 13, 15, O)                      # snout bottom
    rect(px, 11, 12, 12, 13, O)                      # nose

    # Cheek shadow (subtle, one tone)
    px += [(7, 9, D), (16, 9, D)]

    # Neck
    rect(px, 10, 16, 13, 17, B); px += [(9, 16, O), (9, 17, O), (14, 16, O), (14, 17, O), (13, 16, D), (13, 17, D)]

    # Shoulders / shirt
    SB, SO = (D, O) if shirt is None else shirt
    rect(px, 7, 18, 16, 18, SB); rect(px, 5, 19, 18, 19, SB); rect(px, 3, 20, 20, 20, SB)
    rect(px, 1, 21, 22, 21, SB); rect(px, 0, 22, 23, 23, SB)
    px += [(7, 18, SO), (16, 18, SO), (5, 19, SO), (18, 19, SO)]
    rect(px, 3, 20, 4, 20, SO); rect(px, 19, 20, 20, 20, SO)
    rect(px, 1, 21, 2, 21, SO); rect(px, 21, 21, 22, 21, SO)
    rect(px, 0, 22, 1, 22, SO); rect(px, 22, 22, 23, 22, SO)
    if shirt is not None:
        rect(px, 10, 18, 13, 18, B); rect(px, 11, 19, 12, 19, B)
    return px


# ── Eyes (cols 9 + 13, row 8) ─────────────────────────────────────────────
def eyes(kind):
    O, W = INK, CREAM
    px = []
    for ex, far in [(9, False), (13, True)]:
        ey = 8
        if kind == "Normal":
            px += [(ex, ey, W), (ex + 1, ey, W), (ex, ey + 1, O), (ex + 1, ey + 1, W)]
        elif kind == "Sleepy":
            px += [(ex, ey + 1, O), (ex + 1, ey + 1, O)]
        elif kind == "Blank":
            rect(px, ex, ey, ex + 1, ey + 1, W)
        elif kind == "Wink":
            if not far: px += [(ex, ey, W), (ex + 1, ey, W), (ex, ey + 1, O), (ex + 1, ey + 1, W)]
            else: px += [(ex, ey + 1, O), (ex + 1, ey + 1, O)]
        elif kind == "Laser":
            rect(px, ex, ey, ex + 1, ey + 1, ACCENT); px += [(ex - 1, ey, ACCENT), (ex - 2, ey, ACCENT_L)]
        elif kind == "Shades":
            rect(px, ex - 1, ey, ex + 1, ey + 1, INK); px.append((ex, ey, CREAM))
    if kind == "Shades":
        px += [(11, 8, INK), (12, 8, INK)]
    return px


# ── Mouth (centred snout, rows 13-15) ─────────────────────────────────────
def mouth(kind):
    O = INK
    px = []
    if kind == "Smile":
        px += [(10, 14, O), (11, 15, O), (12, 15, O), (13, 14, O)]
    elif kind == "Neutral":
        px += [(10, 14, O), (11, 14, O), (12, 14, O), (13, 14, O)]
    elif kind == "Tongue":
        px += [(10, 14, O), (11, 15, O), (12, 15, O), (13, 14, O),
               (11, 15, ACCENT_L), (12, 15, ACCENT_L)]
    elif kind == "Fang":
        px += [(10, 14, O), (11, 15, O), (12, 15, O), (13, 14, O), (10, 15, CREAM), (13, 15, CREAM)]
    return px


def hat(kind):
    O = INK
    px = []
    if kind == "None":
        return px
    if kind == "Beanie":
        for x in range(6, 18): px.append((x, 3, ACCENT))
        for x in range(7, 17): px.append((x, 2, ACCENT))
        for x in range(8, 16): px.append((x, 1, ACCENT))
        px += [(11, 0, CREAM), (12, 0, CREAM)]
        for x in range(6, 18): px.append((x, 4, O))
    elif kind == "Cap":
        for x in range(7, 17): px += [(x, 2, INK), (x, 3, INK)]
        for x in range(15, 19): px.append((x, 4, INK))      # peak right
        rect(px, 10, 3, 13, 3, ACCENT)
        for x in range(7, 17): px.append((x, 4, O))
    elif kind == "Crown":
        for i in range(5):
            x = 7 + i * 2; px += [(x, 3, GOLD), (x, 2, GOLD), (x, 1, GOLD)]
        for x in range(7, 17): px.append((x, 3, GOLD))
        for x in range(7, 17): px.append((x, 4, O))
        px += [(11, 3, ACCENT), (12, 3, ACCENT)]
    elif kind == "Halo":
        for x in range(8, 16): px.append((x, 0, GOLD))
        px += [(7, 1, GOLD), (16, 1, GOLD)]
    elif kind == "Cone":
        px += [(12, 0, ACCENT), (11, 1, ACCENT), (12, 1, ACCENT),
               (10, 2, ACCENT), (11, 2, CREAM), (12, 2, ACCENT), (13, 2, ACCENT),
               (10, 3, ACCENT), (11, 3, ACCENT), (12, 3, CREAM), (13, 3, ACCENT), (14, 3, ACCENT)]
        for x in range(9, 15): px.append((x, 4, O))
    return px


def accessory(kind):
    O = INK
    px = []
    if kind == "None":
        return px
    if kind == "Cigar":
        px += [(14, 14, O), (15, 14, O), (16, 14, O), (17, 14, ACCENT), (17, 13, ACCENT_L), (18, 12, CREAM)]
    elif kind == "Bone":
        for x in range(8, 16): px.append((x, 14, CREAM))
        px += [(8, 13, CREAM), (15, 13, CREAM), (8, 15, CREAM), (15, 15, CREAM), (7, 14, O), (16, 14, O)]
    elif kind == "Collar":
        for x in range(9, 15): px.append((x, 17, ACCENT))
        for x in range(9, 15): px.append((x, 18, O) if False else (x, 17, ACCENT))
        px += [(11, 17, GOLD), (12, 17, GOLD)]
    elif kind == "Chain":
        for x in range(6, 18): px.append((x, 19, GOLD if x % 2 == 0 else "#e6c87e"))
        rect(px, 10, 20, 13, 21, GOLD); px += [(11, 21, O), (12, 21, O)]
    elif kind == "Bandana":
        for x in range(7, 17): px += [(x, 5, ACCENT), (x, 4, ACCENT)]
        px += [(16, 6, ACCENT), (17, 6, ACCENT)]
        for x in range(7, 17): px.append((x, 6, O))
    return px


# ── trait weights ─────────────────────────────────────────────────────────
W = {
 "Background": dict(zip(BGS, [34, 18, 16, 16, 16])),
 "Fur": dict(zip(FURS, [24, 18, 16, 13, 10, 9, 6, 4])),
 "Shirt": dict(zip(SHIRTS, [28, 18, 16, 14, 14, 10])),
 "Eyes": {"Normal": 26, "Shades": 24, "Sleepy": 14, "Wink": 12, "Laser": 9, "Blank": 9, "Tired": 6},
 "Mouth": {"Smile": 30, "Neutral": 24, "Tongue": 22, "Fang": 24},
 "Hat": {"None": 34, "Cap": 16, "Beanie": 16, "Bandana": 12, "Crown": 10, "Halo": 6, "Cone": 6},
 "Accessory": {"None": 40, "Chain": 22, "Cigar": 16, "Collar": 12, "Bone": 10},
}
# alias: keep "Tired" working as Sleepy variant by mapping in eyes()
W["Eyes"].pop("Tired", None)


def pick(rng, layer):
    o = W[layer]; tot = sum(o.values()); r = rng.uniform(0, tot); up = 0
    for k, v in o.items():
        up += v
        if r <= up: return k
    return list(o)[-1]


def compose(t):
    px = base_portrait(FURS[t["Fur"]], SHIRTS[t["Shirt"]])
    px += eyes(t["Eyes"]); px += mouth(t["Mouth"]); px += hat(t["Hat"]); px += accessory(t["Accessory"])
    return px


def render_png(t, scale=24):
    img = Image.new("RGB", (GRID, GRID), BGS[t["Background"]])
    for x, y, c in compose(t):
        if 0 <= x < GRID and 0 <= y < GRID:
            img.putpixel((x, y), tuple(int(c[i:i+2], 16) for i in (1, 3, 5)))
    return img.resize((GRID * scale, GRID * scale), Image.NEAREST)


def svg_string(t, size=1024):
    body = "".join(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{c}"/>' for x, y, c in compose(t))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="{size}" height="{size}" '
            f'shape-rendering="crispEdges" style="background:{BGS[t["Background"]]};image-rendering:pixelated">' + body + "</svg>")


def sample(n, seed):
    rng = random.Random(seed); seen, toks = set(), []
    while len(toks) < n and len(seen) < n * 60:
        t = {L: pick(rng, L) for L in W}
        key = tuple(t.values())
        if key in seen: continue
        seen.add(key); toks.append({"token_id": len(toks), "traits": t})
    return toks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", type=int); ap.add_argument("--collection", type=int)
    ap.add_argument("--seed", type=int, default=6969)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if a.preview:
        toks = sample(a.preview, a.seed); cols = 4; rows = (a.preview + 3) // 4; cell = 240
        sheet = Image.new("RGB", (cols * cell, rows * cell), (22, 22, 26))
        for i, t in enumerate(toks):
            sheet.paste(render_png(t["traits"]).resize((cell, cell), Image.NEAREST), ((i % cols) * cell, (i // cols) * cell))
        sheet.save(OUT / "preview.png"); print("preview ->", OUT / "preview.png")
    else:
        n = a.collection or 5555; toks = sample(n, a.seed)
        (OUT / "images").mkdir(exist_ok=True); (OUT / "svg").mkdir(exist_ok=True); (OUT / "metadata").mkdir(exist_ok=True)
        for t in toks:
            render_png(t["traits"], 24).save(OUT / "images" / f"{t['token_id']}.png")
            (OUT / "svg" / f"{t['token_id']}.svg").write_text(svg_string(t["traits"]), encoding="utf-8")
            (OUT / "metadata" / f"{t['token_id']}.json").write_text(json.dumps({
                "name": f"ROBARK #{t['token_id']}", "image": f"ipfs://CID/{t['token_id']}.png",
                "attributes": [{"trait_type": k, "value": v} for k, v in t["traits"].items()]}, indent=2))
        print(f"[OK] {len(toks)} -> {OUT}")


if __name__ == "__main__":
    main()
