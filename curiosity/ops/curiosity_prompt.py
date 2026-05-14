#!/usr/bin/env python3
from __future__ import annotations
import json
import random
import pathlib
from datetime import datetime, timezone

REPO = pathlib.Path("/home/luma/.openclaw/workspace/luma-journal")
CURIOSITY_DIR = REPO / "curiosity"
TEMPLATES = CURIOSITY_DIR / "templates" / "prompts.md"
OUTBOX = CURIOSITY_DIR / "outbox"

# Config defaults (state stored locally, untracked)
CONFIG = {
    "max_per_day": 2,
    "min_hours_between": 6,
}

def load_templates():
    text = TEMPLATES.read_text(encoding="utf-8")
    # naive split by blank lines into templates
    parts = [p.strip() for p in text.split('\n\n') if p.strip()]
    templates = []
    for p in parts:
        lines = p.splitlines()
        body = lines[0].strip()
        templates.append(body)
    return templates

def render_sample(templates):
    tpl = random.choice(templates)
    # simple topic filler
    topic = random.choice(["reading", "tools", "a small habit", "a project"]) 
    body = tpl.replace("{topic}", topic)
    # ensure 3-8 lines: wrap into lines by sentences
    lines = [l.strip() for l in body.split('.') if l.strip()]
    if len(lines) < 2:
        lines = [body]
    return "\n\n".join(lines[:6])

def write_outbox(content):
    OUTBOX.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    name = now.strftime('%Y-%m-%d-%H%M%S') + '.md'
    path = OUTBOX / name
    meta = {
        'generated_at': now.isoformat(),
        'mode': 'dry-run',
    }
    text = f"---\n{json.dumps(meta)}\n---\n\n{content}\n"
    # atomic write
    tmp = path.with_suffix('.tmp')
    tmp.write_text(text, encoding='utf-8')
    tmp.rename(path)
    return path

if __name__ == '__main__':
    templates = load_templates()
    sample = render_sample(templates)
    p = write_outbox(sample)
    print(p)
