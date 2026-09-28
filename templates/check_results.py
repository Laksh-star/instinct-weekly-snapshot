#!/usr/bin/env python3
"""Fail a candidate weekly snapshot when the private journal's Results rows are absent.

Inclusion check only. Human source verification and edition-specific approval still apply.
"""
from pathlib import Path
import html
import re
import sys

if len(sys.argv) != 3:
    raise SystemExit("usage: check_results.py README.md candidate.html")
readme = Path(sys.argv[1]).read_text(encoding="utf-8")
page = html.unescape(Path(sys.argv[2]).read_text(encoding="utf-8"))
section = re.search(r"(?ms)^## Results\s*\n(.*?)(?=^## |\Z)", readme)
if not section:
    raise SystemExit("README Results section missing")
rows = []
for line in section.group(1).splitlines():
    if not line.startswith("|") or "---" in line or "Workstream | Metric" in line:
        continue
    cells = [c.strip() for c in line.strip("|").split("|")]
    if len(cells) < 4:
        raise SystemExit(f"Malformed Results row: {line}")
    rows.append(cells[:4])
if len(rows) < 9 or {r[0] for r in rows if r[0]} != {"DBCA client pipeline", "WatchWise", "Thirst"}:
    raise SystemExit("Unexpected Results workstreams or row count")
visible = re.sub(r"<[^>]+>", " ", re.sub(r"(?s)<(?:script|style)\b.*?</(?:script|style)>", " ", page))
visible = re.sub(r"\s+", " ", visible)
missing = [f"{r[1]}: {r[2]}" for r in rows if r[1] not in visible or r[2] not in visible]
missing.extend(name for name in ("DBCA client pipeline", "WatchWise", "Thirst") if name not in visible)
if missing:
    raise SystemExit("Results absent from candidate: " + "; ".join(missing))
print(f"Included all {len(rows)} README Results rows in candidate. Verify sources and obtain edition approval separately.")
