"""
Thin ComfyUI HTTP client. Submits a workflow graph with the prompt/seed patched
in, waits for completion, and downloads the resulting PNG.

ComfyUI runs on the RunPod GPU pod (default port 8188). Point COMFY_URL at it.
The workflow graph lives in runpod/workflows/pixel_shiba.json — export your own
from the ComfyUI UI and keep the node ids in sync with NODE_IDS below.
"""
from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path

COMFY_URL = os.environ.get("COMFY_URL", "http://127.0.0.1:8188")

# Node ids in the workflow JSON that we patch per-token.
NODE_IDS = {
    "positive": os.environ.get("COMFY_NODE_POSITIVE", "6"),
    "negative": os.environ.get("COMFY_NODE_NEGATIVE", "7"),
    "sampler": os.environ.get("COMFY_NODE_SAMPLER", "3"),
    "save": os.environ.get("COMFY_NODE_SAVE", "9"),
}


class ComfyClient:
    def __init__(self, base_url: str = COMFY_URL, workflow_path: Path | None = None):
        self.base = base_url.rstrip("/")
        root = Path(__file__).resolve().parent.parent
        self.workflow_path = workflow_path or root / "workflows" / "pixel_shiba.json"
        self.template = json.loads(self.workflow_path.read_text(encoding="utf-8"))

    def _post(self, path: str, payload: dict) -> dict:
        req = urllib.request.Request(
            f"{self.base}{path}",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())

    def _get(self, path: str) -> dict:
        with urllib.request.urlopen(f"{self.base}{path}", timeout=120) as r:
            return json.loads(r.read())

    def _patch_graph(self, positive: str, negative: str, seed: int) -> dict:
        g = json.loads(json.dumps(self.template))  # deep copy
        g[NODE_IDS["positive"]]["inputs"]["text"] = positive
        g[NODE_IDS["negative"]]["inputs"]["text"] = negative
        g[NODE_IDS["sampler"]]["inputs"]["seed"] = seed
        return g

    def generate(self, positive: str, negative: str, seed: int, out_path: Path,
                 poll: float = 1.0, timeout: float = 300.0) -> Path:
        graph = self._patch_graph(positive, negative, seed)
        resp = self._post("/prompt", {"prompt": graph})
        prompt_id = resp["prompt_id"]

        deadline = time.time() + timeout
        while time.time() < deadline:
            hist = self._get(f"/history/{prompt_id}")
            if prompt_id in hist:
                outputs = hist[prompt_id]["outputs"]
                images = outputs.get(NODE_IDS["save"], {}).get("images", [])
                if images:
                    img = images[0]
                    self._download(img["filename"], img.get("subfolder", ""),
                                   img.get("type", "output"), out_path)
                    return out_path
            time.sleep(poll)
        raise TimeoutError(f"ComfyUI generation timed out for prompt {prompt_id}")

    def _download(self, filename: str, subfolder: str, ftype: str, out_path: Path):
        q = urllib.parse.urlencode(
            {"filename": filename, "subfolder": subfolder, "type": ftype}
        )
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(f"{self.base}/view?{q}", timeout=120) as r:
            out_path.write_bytes(r.read())
