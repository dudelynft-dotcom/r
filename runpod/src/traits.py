"""
Trait engine for ROBARK.

Loads the YAML taxonomy and samples N *unique* trait combinations with a fixed
seed (so the whole collection is reproducible). Also computes rarity scores.

This module is pure-Python and needs no GPU — run it first to produce the trait
DNA for all 10,000 tokens, then feed that DNA to the image generator.
"""
from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
TRAITS_FILE = ROOT / "traits" / "traits.yaml"


@dataclass
class Option:
    value: str
    weight: float
    prompt: str


@dataclass
class Layer:
    name: str
    options: list[Option]

    def weighted_choice(self, rng: random.Random) -> Option:
        total = sum(o.weight for o in self.options)
        r = rng.uniform(0, total)
        upto = 0.0
        for o in self.options:
            upto += o.weight
            if r <= upto:
                return o
        return self.options[-1]


@dataclass
class Taxonomy:
    name: str
    size: int
    base_prompt: str
    base_negative: str
    layers: list[Layer]

    @classmethod
    def load(cls, path: Path = TRAITS_FILE) -> "Taxonomy":
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        coll = data["collection"]
        layers = []
        for ldef in data["layers"]:
            opts = [
                Option(
                    value=o["value"],
                    weight=float(o["weight"]),
                    prompt=o.get("prompt", "") or "",
                )
                for o in ldef["weights"]
            ]
            layers.append(Layer(name=ldef["name"], options=opts))
        return cls(
            name=coll["name"],
            size=int(coll["size"]),
            base_prompt=" ".join(coll["base_prompt"].split()),
            base_negative=" ".join(coll["base_negative"].split()),
            layers=layers,
        )


@dataclass
class Token:
    token_id: int
    traits: dict[str, str]  # layer name -> value
    dna: str = ""
    rarity_score: float = 0.0
    rank: int = 0
    prompts: dict[str, str] = field(default_factory=dict)


def _dna(traits: dict[str, str]) -> str:
    raw = "|".join(f"{k}={v}" for k, v in sorted(traits.items()))
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def sample_collection(tax: Taxonomy, size: int | None = None, seed: int = 42) -> list[Token]:
    """Sample `size` unique trait combinations deterministically."""
    size = size or tax.size
    rng = random.Random(seed)
    seen: set[str] = set()
    tokens: list[Token] = []
    attempts = 0
    max_attempts = size * 50

    while len(tokens) < size and attempts < max_attempts:
        attempts += 1
        combo = {layer.name: layer.weighted_choice(rng).value for layer in tax.layers}
        dna = _dna(combo)
        if dna in seen:
            continue
        seen.add(dna)
        tokens.append(Token(token_id=len(tokens), traits=combo, dna=dna))

    if len(tokens) < size:
        raise RuntimeError(
            f"Only generated {len(tokens)}/{size} unique combos — widen the "
            f"taxonomy (more layers/options) to increase the combination space."
        )
    return tokens


def compute_rarity(tax: Taxonomy, tokens: list[Token]) -> None:
    """Assign rarity score (sum of 1/trait-frequency) and rank in-place."""
    counts: dict[tuple[str, str], int] = {}
    n = len(tokens)
    for t in tokens:
        for layer, value in t.traits.items():
            counts[(layer, value)] = counts.get((layer, value), 0) + 1

    for t in tokens:
        score = 0.0
        for layer, value in t.traits.items():
            freq = counts[(layer, value)] / n
            score += 1.0 / freq
        t.rarity_score = round(score, 4)

    for rank, t in enumerate(sorted(tokens, key=lambda x: x.rarity_score, reverse=True), start=1):
        t.rank = rank


def trait_frequencies(tax: Taxonomy, tokens: list[Token]) -> dict[str, Any]:
    n = len(tokens)
    out: dict[str, Any] = {}
    for layer in tax.layers:
        layer_counts: dict[str, int] = {}
        for t in tokens:
            v = t.traits[layer.name]
            layer_counts[v] = layer_counts.get(v, 0) + 1
        out[layer.name] = {
            v: {"count": c, "percent": round(100 * c / n, 3)}
            for v, c in sorted(layer_counts.items(), key=lambda kv: -kv[1])
        }
    return out


def save_dna(tokens: list[Token], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [
        {
            "token_id": t.token_id,
            "dna": t.dna,
            "traits": t.traits,
            "rarity_score": t.rarity_score,
            "rank": t.rank,
        }
        for t in tokens
    ]
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Generate ROBARK trait DNA")
    p.add_argument("--size", type=int, default=None, help="how many tokens")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", type=Path, default=ROOT / "output" / "dna.json")
    args = p.parse_args()

    tax = Taxonomy.load()
    toks = sample_collection(tax, size=args.size, seed=args.seed)
    compute_rarity(tax, toks)
    save_dna(toks, args.out)

    freqs = trait_frequencies(tax, toks)
    (args.out.parent / "rarity_report.json").write_text(
        json.dumps(freqs, indent=2), encoding="utf-8"
    )
    print(f"[OK] {len(toks)} unique tokens -> {args.out}")
    print(f"[OK] rarity report -> {args.out.parent / 'rarity_report.json'}")
