"""Build Stable Diffusion prompts from a token's trait DNA."""
from __future__ import annotations

from .traits import Option, Taxonomy, Token


def _option_for(tax: Taxonomy, layer_name: str, value: str) -> Option | None:
    for layer in tax.layers:
        if layer.name == layer_name:
            for o in layer.options:
                if o.value == value:
                    return o
    return None


def build_prompt(tax: Taxonomy, token: Token) -> tuple[str, str]:
    """Return (positive_prompt, negative_prompt) for the given token."""
    parts: list[str] = [tax.base_prompt]
    # order layers so fur/eyes/mouth come before accessories for coherence
    for layer in tax.layers:
        value = token.traits.get(layer.name)
        if not value:
            continue
        opt = _option_for(tax, layer.name, value)
        if opt and opt.prompt.strip():
            parts.append(opt.prompt.strip())
    positive = ", ".join(parts)
    return positive, tax.base_negative
