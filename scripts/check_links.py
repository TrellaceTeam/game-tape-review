#!/usr/bin/env python3
"""Check that every relative link and anchor in the repo's Markdown resolves.

Run from the repo root: python scripts/check_links.py

Web links are left alone, so the check is fast and gives the same answer
offline. Anchors are checked against GitHub's heading slugs.
"""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build"}
FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_LINK = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
REF_DEF = re.compile(r"^\s*\[[^\]]+\]:\s*<?(\S+?)>?(?:\s+\"[^\"]*\")?\s*$")
HTML_SRC = re.compile(r"""(?:src|href)=["']([^"']+)["']""")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
HTML_ANCHOR = re.compile(r"""<a\s+(?:name|id)=["']([^"']+)["']""")
EXTERNAL = ("http://", "https://", "mailto:", "tel:", "data:")


def slug(heading: str) -> str:
    text = re.sub(r"`([^`]*)`", r"\1", heading)
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = unicodedata.normalize("NFKC", text).lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def anchors_in(path: Path, cache: dict[Path, set[str]]) -> set[str]:
    if path in cache:
        return cache[path]
    found: set[str] = set()
    counts: dict[str, int] = {}
    in_fence = False
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for name in HTML_ANCHOR.findall(line):
            found.add(name)
        match = HEADING.match(line)
        if match:
            base = slug(match.group(2))
            n = counts.get(base, 0)
            found.add(base if n == 0 else f"{base}-{n}")
            counts[base] = n + 1
    cache[path] = found
    return found


def links_in(path: Path) -> list[tuple[int, str]]:
    links = []
    in_fence = False
    for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        stripped = re.sub(r"`[^`]*`", "", line)
        for pattern in (INLINE_LINK, HTML_SRC):
            links.extend((number, target) for target in pattern.findall(stripped))
        ref = REF_DEF.match(stripped)
        if ref:
            links.append((number, ref.group(1)))
    return links


def main() -> int:
    root = Path.cwd()
    cache: dict[Path, set[str]] = {}
    problems = []
    files = sorted(
        p for p in root.rglob("*.md")
        if not any(part in SKIP_DIRS for part in p.relative_to(root).parts)
    )
    for path in files:
        for number, target in links_in(path):
            if target.startswith(EXTERNAL) or target.startswith("{{"):
                continue
            target_path, _, anchor = target.partition("#")
            target_path = unquote(target_path.split("?", 1)[0])
            if target_path:
                resolved = (root / target_path.lstrip("/")) if target_path.startswith("/") else (path.parent / target_path)
                resolved = resolved.resolve()
                if not resolved.exists():
                    problems.append(f"{path.relative_to(root).as_posix()}:{number}: missing file: {target}")
                    continue
            else:
                resolved = path
            if anchor and resolved.suffix == ".md" and anchor not in anchors_in(resolved, cache):
                problems.append(f"{path.relative_to(root).as_posix()}:{number}: missing anchor: {target}")
    for problem in problems:
        print(problem)
    print(f"check_links: {len(files)} files, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
