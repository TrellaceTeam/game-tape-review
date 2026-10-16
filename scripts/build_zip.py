#!/usr/bin/env python3
"""Build dist/game-tape.zip for upload to Claude, ChatGPT or any skills tool.

Run from the repo root: python scripts/build_zip.py

The zip holds the game-tape folder at its root, the shape Claude requires, with
forward-slash paths so it opens the same on Mac, Windows and Linux. Files are
sorted and dated the same way each run, so an unchanged skill builds the same zip.
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "game-tape"
OUT = ROOT / "dist" / "game-tape.zip"
SKIP = {"__pycache__", ".DS_Store"}


def build() -> Path:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    # A team/ folder is someone's own setup, from a local test, and never ships.
    files = sorted(p for p in SKILL.rglob("*") if p.is_file() and not SKIP & set(p.parts) and p.suffix != ".pyc"
                   and p.relative_to(SKILL).parts[0] != "team")
    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            name = "game-tape/" + path.relative_to(SKILL).as_posix()
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes())
    return OUT


def main() -> int:
    out = build()
    with zipfile.ZipFile(out) as archive:
        names = archive.namelist()
    if "game-tape/SKILL.md" not in names or any(not n.startswith("game-tape/") for n in names):
        print("zip shape is wrong: every entry must start with game-tape/ and SKILL.md must be in it")
        return 1
    print(f"wrote {out.relative_to(ROOT).as_posix()}: {len(names)} files")
    for name in names:
        print(f"  {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
