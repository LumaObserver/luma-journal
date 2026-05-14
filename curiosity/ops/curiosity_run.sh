#!/usr/bin/env bash
set -euo pipefail
REPO="/home/luma/.openclaw/workspace/luma-journal"
cd "$REPO"
# Dry-run mode: generate sample pulse only, do not send
python3 curiosity/ops/curiosity_prompt.py
exit 0
