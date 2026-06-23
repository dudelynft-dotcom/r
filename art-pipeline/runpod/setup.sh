#!/usr/bin/env bash
# One-time setup on a RunPod GPU pod (PyTorch template recommended).
set -euo pipefail
cd "$(dirname "$0")"

echo "==> Installing deps"
pip install -q -r requirements.txt

echo "==> Hugging Face login (FLUX.1-dev is gated — accept its license on HF first)"
echo "    Run:  huggingface-cli login    (paste your HF token)"
echo "    Accept: https://huggingface.co/black-forest-labs/FLUX.1-dev"

echo "==> Done. Then render with:"
echo "    python generate_flat.py            # all 5555"
echo "    python generate_flat.py --offload  # if GPU < 40GB (e.g. RTX 4090)"
