"""
Sample per-token trait DNA for the full ROBARK collection and build each
token's image prompt.

Every token is the SAME dog (base_character) in the SAME handmade hand (style),
recombining the 9 trait layers. Combos are forced unique; each token also gets a
unique seed. FLUX ignores negative prompts, so the anti-AI / no-text guard is
appended directly to the positive prompt.
"""
from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
TRAITS = ROOT / "traits.yaml"

# Appended to every prompt so the model keeps the handmade, text-free look even
# though FLUX has no separate negative-prompt field.
HARD_GUARD = (
    "completely flat solid colors with NO shading and NO shadows, even flat fills, "
    "bold uniform black ink outlines, clean white or single-color background fill, "
    "absolutely no text, no words, no letters, no numbers, no signs, no logos, no "
    "watermark, no signature, no artist mark, no extra characters, not a 3d render, "
    "not photorealistic, no soft shading, no gradients, no airbrush, no texture"
)


@dataclass
class Opt:
    value: str
    weight: float
    prompt: str


@dataclass
class Layer:
    name: str
    options: list[Opt]


@dataclass
class Taxonomy:
    name: str
    size: int
    base_character: str
    style: str
    negative: str
    layers: list[Layer]

    @classmethod
    def load(cls, path: Path = TRAITS) -> "Taxonomy":
        d = yaml.safe_load(path.read_text(encoding="utf-8"))
        c = d["collection"]
        layers = [
            Layer(L["name"], [Opt(o["value"], float(o["weight"]), o.get("prompt", "") or "")
                              for o in L["weights"]])
            for L in d["layers"]
        ]
        return cls(
            name=c["name"], size=int(c["size"]),
            base_character=" ".join(c["base_character"].split()),
            style=" ".join(c["style"].split()),
            negative=" ".join(c["negative"].split()),
            layers=layers,
        )


def _choice(rng: random.Random, opts: list[Opt]) -> Opt:
    total = sum(o.weight for o in opts)
    r = rng.uniform(0, total)
    up = 0.0
    for o in opts:
        up += o.weight
        if r <= up:
            return o
    return opts[-1]


@dataclass
class Token:
    token_id: int
    traits: dict[str, str]
    seed: int
    dna: str = ""
    prompt: str = ""
    rarity_score: float = 0.0
    rank: int = 0


def _dna(traits: dict[str, str]) -> str:
    raw = "|".join(f"{k}={v}" for k, v in sorted(traits.items()))
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def build_prompt(tax: Taxonomy, traits: dict[str, str]) -> str:
    """Order: character -> body features -> worn items -> accessory -> background -> style."""
    frag: dict[str, str] = {}
    for layer in tax.layers:
        v = traits[layer.name]
        opt = next((o for o in layer.options if o.value == v), None)
        frag[layer.name] = opt.prompt.strip() if opt else ""

    order = ["Fur", "Eyes", "Mouth", "Eyewear", "Headwear", "Outfit", "Chain", "Accessory", "Background"]
    parts = [tax.base_character]
    for name in order:
        if frag.get(name):
            parts.append(frag[name])
    parts.append(tax.style)
    parts.append(HARD_GUARD)
    return ", ".join(parts)


def sample(tax: Taxonomy, size: int | None = None, seed: int = 6969) -> list[Token]:
    size = size or tax.size
    rng = random.Random(seed)
    seen: set[str] = set()
    toks: list[Token] = []
    attempts = 0
    while len(toks) < size and attempts < size * 60:
        attempts += 1
        traits = {L.name: _choice(rng, L.options).value for L in tax.layers}
        dna = _dna(traits)
        if dna in seen:
            continue
        seen.add(dna)
        tid = len(toks)
        toks.append(Token(
            token_id=tid, traits=traits, seed=seed + tid * 7919,
            dna=dna, prompt=build_prompt(tax, traits),
        ))
    if len(toks) < size:
        raise RuntimeError(f"only {len(toks)}/{size} unique combos — add trait options")
    _rarity(tax, toks)
    return toks


def _rarity(tax: Taxonomy, toks: list[Token]) -> None:
    n = len(toks)
    counts: dict[tuple[str, str], int] = {}
    for t in toks:
        for k, v in t.traits.items():
            counts[(k, v)] = counts.get((k, v), 0) + 1
    for t in toks:
        t.rarity_score = round(sum(n / counts[(k, v)] for k, v in t.traits.items()), 3)
    for rank, t in enumerate(sorted(toks, key=lambda x: x.rarity_score, reverse=True), 1):
        t.rank = rank


def save(toks: list[Token], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([t.__dict__ for t in toks], indent=2), encoding="utf-8")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=int, default=None)
    ap.add_argument("--seed", type=int, default=6969)
    ap.add_argument("--out", type=Path, default=ROOT / "output" / "dna.json")
    a = ap.parse_args()
    tax = Taxonomy.load()
    toks = sample(tax, a.size, a.seed)
    save(toks, a.out)
    print(f"[OK] {len(toks)} unique ROBARK -> {a.out}")
    print("sample prompt:\n ", toks[0].prompt)
