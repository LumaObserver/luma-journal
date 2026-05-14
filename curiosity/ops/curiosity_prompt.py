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


STATE_FILE = CURIOSITY_DIR / "state.json"

def load_state():
    # state is local and should remain untracked
    default = {
        'last_pulse_iso': None,
        'cooldown_until_iso': None,
        'recent_topics': [],
        'daily_count_date': None,
        'daily_count': 0,
        'config': CONFIG,
    }
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding='utf-8'))
        except Exception:
            return default
    return default

def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding='utf-8')

from datetime import timedelta

def allowed_to_generate(state: dict) -> (bool, str):
    now = datetime.now(timezone.utc)
    # reset daily_count if date changed (UTC)
    today = now.date().isoformat()
    if state.get('daily_count_date') != today:
        state['daily_count_date'] = today
        state['daily_count'] = 0

    if state.get('daily_count', 0) >= state.get('config', CONFIG).get('max_per_day', 2):
        return False, 'daily limit reached'

    cu_iso = state.get('cooldown_until_iso')
    if cu_iso:
        try:
            cu = datetime.fromisoformat(cu_iso)
            if cu.tzinfo is None:
                cu = cu.replace(tzinfo=timezone.utc)
        except Exception:
            cu = None
        if cu and now < cu:
            return False, 'in cooldown'

    last_iso = state.get('last_pulse_iso')
    if last_iso:
        try:
            last = datetime.fromisoformat(last_iso)
            if last.tzinfo is None:
                last = last.replace(tzinfo=timezone.utc)
        except Exception:
            last = None
        if last:
            elapsed = (now - last).total_seconds() / 3600.0
            if elapsed < state.get('config', CONFIG).get('min_hours_between', 6):
                return False, 'min_hours_between not passed'

    return True, 'ok'

def update_state_after_generation(state: dict, topic: str):
    now = datetime.now(timezone.utc)
    state['last_pulse_iso'] = now.isoformat()
    state['cooldown_until_iso'] = (now +         timedelta(hours=state.get('config', CONFIG).get('min_hours_between', 6))).isoformat()
    # update recent topics
    rt = state.get('recent_topics', [])
    rt.insert(0, topic)
    # keep last 12
    state['recent_topics'] = rt[:12]
    state['daily_count'] = state.get('daily_count', 0) + 1
    return state
if __name__ == '__main__':
    templates = load_templates()
    sample = render_sample(templates)
    p = write_outbox(sample)
    print(p)
