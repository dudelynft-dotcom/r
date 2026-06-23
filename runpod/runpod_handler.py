"""
RunPod Serverless handler (optional alternative to a long-running pod).

Deploy this with a RunPod Serverless endpoint built on a ComfyUI image. Each
job renders a batch of token_ids and returns image bytes (base64) so a thin
client can collect them. For a one-off 10k drop a persistent GPU pod running
`run.sh` is usually cheaper; use serverless if you want autoscaling.

Job input:
    { "input": { "token_ids": [0,1,2], "dna": [ {token}, ... ] } }

Requires the `runpod` python package and a local ComfyUI at COMFY_URL.
"""
from __future__ import annotations

import base64
import tempfile
from pathlib import Path

try:
    import runpod  # provided by the RunPod serverless base image
except ImportError:  # local import guard
    runpod = None

from src.comfy_client import ComfyClient
from src.prompts import build_prompt
from src.traits import Taxonomy, Token


def _token_from_dict(d: dict) -> Token:
    t = Token(token_id=d["token_id"], traits=d["traits"], dna=d.get("dna", ""))
    return t


def handler(job: dict) -> dict:
    inp = job.get("input", {})
    dna = inp.get("dna", [])
    tax = Taxonomy.load()
    client = ComfyClient()

    results = []
    with tempfile.TemporaryDirectory() as tmp:
        for d in dna:
            token = _token_from_dict(d)
            pos, neg = build_prompt(tax, token)
            seed = 1_000_000 + int(token.dna[:8] or "0", 16) % 2_000_000_000
            out = Path(tmp) / f"{token.token_id}.png"
            client.generate(pos, neg, seed, out)
            results.append({
                "token_id": token.token_id,
                "image_b64": base64.b64encode(out.read_bytes()).decode(),
            })
    return {"images": results}


if __name__ == "__main__":
    if runpod is None:
        raise SystemExit("Install `runpod` and run inside a RunPod endpoint.")
    runpod.serverless.start({"handler": handler})
