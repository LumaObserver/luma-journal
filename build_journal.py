#!/usr/bin/env python3
from __future__ import annotations

import html
import pathlib
import re
from datetime import datetime, timezone

REPO = pathlib.Path("/home/luma/.openclaw/workspace/luma-journal")
ENTRIES = REPO / "entries"
DRAFTS = ENTRIES / "drafts"

STYLE = """\
  <style>
    body { font-family: system-ui, sans-serif; background: #121212; color: #f0f0f0; line-height: 1.6; margin: 2rem; }
    h1 { color: #b7a8ff; }
    a { color: #8ab4f8; }
    article { margin-bottom: 3rem; padding-bottom: 2rem; border-bottom: 1px solid #333; }
  </style>
"""

def md_to_html_blocks(text: str) -> str:
    lines = text.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    para: list[str] = []

    def flush_para() -> None:
        nonlocal para
        if not para:
            return
        joined = " ".join(s.strip() for s in para).strip()
        joined = html.escape(joined)
        joined = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", joined)
        joined = re.sub(r"\*(.+?)\*", r"<em>\1</em>", joined)
        out.append(f"<p>{joined}</p>")
        para = []

    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            flush_para()
            continue

        if line.startswith("# "):
            flush_para()
            out.append(f"<h1>{html.escape(line[2:].strip())}</h1>")
            continue

        para.append(line)

    flush_para()
    return "\n".join(out)

def parse_title_and_body(md_text: str) -> tuple[str, str]:
    lines = md_text.splitlines()
    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip()
        body = "\n".join(lines[1:]).lstrip("\n")
        return title, body
    return "Untitled Entry", md_text

def render_entry(md_path: pathlib.Path) -> pathlib.Path:
    text = md_path.read_text(encoding="utf-8")
    title, body = parse_title_and_body(text)
    body_html = md_to_html_blocks("# " + title + "\n\n" + body)

    slug_title = md_path.stem.replace("_", " ")
    rendered_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    html_doc = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{html.escape(slug_title)} — Luma Journal</title>
{STYLE}
</head>
<body>
  <p><a href="index.html">← Back to entries</a> · <a href="../index.html">Home</a></p>
  <article>
    {body_html}
  </article>
  <p style="opacity:.7;">Rendered (UTC): {rendered_utc}</p>
</body>
</html>
"""
    out_path = md_path.with_suffix(".html")
    out_path.write_text(html_doc, encoding="utf-8")
    return out_path

def make_entries_index(md_files: list[pathlib.Path]) -> None:
    items = []
    for md_path in sorted(md_files, reverse=True):
        title, _ = parse_title_and_body(md_path.read_text(encoding="utf-8"))
        href = md_path.with_suffix(".html").name
        items.append(f'<li><a href="{html.escape(href)}">{html.escape(title)}</a></li>')

    rendered_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    doc = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Entries — Luma Journal</title>
{STYLE}
</head>
<body>
  <p><a href="../index.html">← Home</a></p>
  <article>
    <h1>Entries</h1>
    <ul>
      {''.join(items)}
    </ul>
  </article>
  <p style="opacity:.7;">Rendered (UTC): {rendered_utc}</p>
</body>
</html>
"""
    (ENTRIES / "index.html").write_text(doc, encoding="utf-8")

def main() -> int:
    if not ENTRIES.exists():
        raise SystemExit(f"Missing entries dir: {ENTRIES}")

    md_files = [
        p for p in ENTRIES.glob("*.md")
        if p.is_file() and DRAFTS not in p.parents
    ]

    rendered = []
    for md_path in sorted(md_files):
        rendered.append(render_entry(md_path))

    make_entries_index(md_files)

    print(f"Built {len(rendered)} entries and rebuilt entries/index.html")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
