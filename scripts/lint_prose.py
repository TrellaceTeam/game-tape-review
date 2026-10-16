#!/usr/bin/env python3
"""Check the repo's Markdown against the house writing rules.

Run from the repo root: python scripts/lint_prose.py [paths...]

Code blocks, inline code, link targets, HTML comments and YAML frontmatter
keys are skipped, so commands and URLs never trip a rule. A word that a file
needs as a literal term can be allowed for one line with an HTML comment on
that line, such as <!-- prose-allow: solution -->, or for the whole repo by
listing it in prose-allow.txt at the repo root, one word per line.
"""

from __future__ import annotations

import fnmatch
import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build"}
SKIP_FILES = {"LICENSE.md", "CHANGELOG.md"}

# Words and phrases that read as filler, hype or machine-written.
BANNED = [
    "additionally", "crucial", "delve", "delves", "delving", "enduring", "enhance", "enhances",
    "enhancing", "fostering", "garner", "interplay", "intricate", "multifaceted", "pivotal",
    "realm", "showcase", "showcases", "tapestry", "testament", "underscore", "underscores",
    "vibrant", "bedrock", "ecosystem", "endgame", "flywheel", "landscape", "locus", "modality",
    "nexus", "north star", "paradigm", "scaffolding", "substrate", "vantage", "empower",
    "empowers", "empowering", "facilitate", "facilitates", "leverage", "leverages", "leveraging",
    "reimagine", "streamline", "streamlines", "streamlined", "supercharge", "turbocharge",
    "unlock", "unlocks", "unlocking", "unpack", "utilize", "utilizes", "utilizing", "all-in-one",
    "best-in-class", "customer-centric", "cutting-edge", "disruptive", "end-to-end",
    "frictionless", "game-changer", "game-changing", "holistic", "industry-leading", "innovative",
    "next-gen", "powerful", "revolutionary", "robust", "seamless", "seamlessly", "synergy",
    "user-friendly", "world-class", "the future of", "welcome to", "align on", "circle back",
    "deep dive", "touch base", "lean in", "value proposition", "with respect to", "in terms of",
    "arguably", "as mentioned", "at the end of the day", "due to the fact that", "in many ways",
    "in order to", "it goes without saying", "it's important to note", "it is important to note",
    "it's no secret", "it's worth noting", "it is worth noting", "needless to say",
    "that being said", "to that end", "with that in mind", "actually", "just", "literally",
    "really", "simply", "truly", "solution", "solutions", "navigate challenges",
]

FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"`[^`]*`")
HTML_COMMENT = re.compile(r"<!--.*?-->")
LINK_TARGET = re.compile(r"\]\([^)]*\)")
REF_DEF = re.compile(r"^\s*\[[^\]]+\]:\s*\S+.*$")
BARE_URL = re.compile(r"https?://\S+")
AUTOLINK = re.compile(r"<https?://[^>]+>")
IMAGE = re.compile(r"!\[[^\]]*\]")
ALERT = re.compile(r"\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]")
HTML_TAG = re.compile(r"<[^>]+>")
ENTITY = re.compile(r"&[a-zA-Z]+;|&#\d+;")
TABLE_RULE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")
ALLOW_INLINE = re.compile(r"<!--\s*prose-allow:\s*([^>]*?)\s*-->")

CHECKS = [
    ("em-dash", re.compile("—"), "use a period or comma"),
    ("en-dash", re.compile("–"), "write 'to' for ranges, a period or comma otherwise"),
    ("double-hyphen", re.compile(r"(?<=\w)--(?=\w)|\s--\s"), "use a period or comma"),
    ("semicolon", re.compile(r";"), "split into two sentences"),
    ("exclamation", re.compile(r"!"), "end on a period"),
    ("curly-quote", re.compile("[‘’“”]"), "use straight quotes"),
]


def load_repo_allow(root: Path) -> set[str]:
    path = root / "prose-allow.txt"
    if not path.exists():
        return set()
    words = set()
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        word = line.split("#", 1)[0].strip().lower()
        if word:
            words.add(word)
    return words


def banned_pattern(words: list[str]) -> re.Pattern[str]:
    alternation = "|".join(re.escape(w).replace(r"\ ", r"\s+") for w in sorted(words, key=len, reverse=True))
    return re.compile(rf"(?<![\w-])({alternation})(?![\w-])", re.IGNORECASE)


def prose_of(line: str) -> str:
    # Drop comments that open and close on this line, then any stray markers of
    # a comment that spans lines, so text kept inside such a comment is still checked.
    text = HTML_COMMENT.sub(" ", line).replace("<!--", " ").replace("-->", " ")
    text = INLINE_CODE.sub(" ", text)
    text = AUTOLINK.sub(" ", text)
    text = LINK_TARGET.sub("]", text)
    text = BARE_URL.sub(" ", text)
    text = IMAGE.sub(" ", text)
    text = ALERT.sub(" ", text)
    text = HTML_TAG.sub(" ", text)
    text = ENTITY.sub(" ", text)
    return text


def lint_file(path: Path, root: Path, repo_allow: set[str]) -> list[str]:
    problems = []
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    in_fence = False
    in_frontmatter = bool(lines) and lines[0].strip() == "---"
    for number, raw in enumerate(lines, start=1):
        if in_frontmatter:
            if number > 1 and raw.strip() == "---":
                in_frontmatter = False
                continue
            if number == 1:
                continue
            # Lint frontmatter values, which are prose, but not keys.
            raw = raw.split(":", 1)[1] if ":" in raw else raw
        if FENCE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence or TABLE_RULE.match(raw) or REF_DEF.match(raw) or raw.strip() in {"---", "***"}:
            continue
        allow = set(repo_allow)
        for match in ALLOW_INLINE.finditer(raw):
            allow.update(w.strip().lower() for w in match.group(1).split(",") if w.strip())
        text = prose_of(raw)
        rel = path.relative_to(root).as_posix()
        for name, pattern, fix in CHECKS:
            if name in allow:
                continue
            hit = pattern.search(text)
            if hit:
                problems.append(f"{rel}:{number}: {name}: {fix}: {raw.strip()[:120]}")
        words = [w for w in BANNED if w not in allow]
        for hit in banned_pattern(words).finditer(text):
            problems.append(f"{rel}:{number}: banned word '{hit.group(1)}': {raw.strip()[:120]}")
    return problems


def load_skips(root: Path) -> list[str]:
    """Glob patterns from prose-skip.txt, for files the house rules don't cover, such as unedited model output."""
    path = root / "prose-skip.txt"
    if not path.exists():
        return []
    return [line.split("#", 1)[0].strip() for line in path.read_text(encoding="utf-8-sig").splitlines()
            if line.split("#", 1)[0].strip()]


def markdown_files(root: Path, targets: list[str]) -> list[Path]:
    if targets:
        found = []
        for target in targets:
            p = (root / target).resolve()
            found.extend(sorted(p.rglob("*.md")) if p.is_dir() else [p])
        return found
    skips = load_skips(root)
    return sorted(
        p for p in root.rglob("*.md")
        if not any(part in SKIP_DIRS for part in p.relative_to(root).parts) and p.name not in SKIP_FILES
        and not any(fnmatch.fnmatch(p.relative_to(root).as_posix(), pattern) for pattern in skips)
    )


def main(argv: list[str]) -> int:
    root = Path.cwd()
    repo_allow = load_repo_allow(root)
    problems = []
    files = markdown_files(root, argv)
    for path in files:
        problems.extend(lint_file(path, root, repo_allow))
    for problem in problems:
        print(problem)
    print(f"lint_prose: {len(files)} files, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
