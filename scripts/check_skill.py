#!/usr/bin/env python3
"""Check a skill folder against the portable skill rules.

Usage:
    python check_skill.py path/to/skill [more/skills ...]
    python check_skill.py --all path/to/skills

Checks, for each skill folder:
- exactly one SKILL.md, at the folder root
- frontmatter with only name, description, license and metadata
- name: lowercase letters, numbers and hyphens, 1 to 64 characters, equal to the folder name
- description: present, single line, under 200 characters
- metadata: a map of strings to strings
- a one-line H1 right after the frontmatter, and SKILL.md under 500 lines
- every relative link in every Markdown file resolves, stays inside the folder,
  and every #anchor matches a heading
- every Python script imports only the standard library, with no shell-outs,
  operating-system branches or network modules, so it runs in a chat app's
  sandbox as well as on a laptop
- the brand appears only in links to github.com/TrellaceTeam and on the
  first-run closing line that carries the session link

Exit code is 0 when every folder passes and 1 otherwise.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote

ALLOWED_KEYS = {"name", "description", "license", "metadata"}
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MAX_DESCRIPTION = 199
MAX_LINES = 500
FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_LINK = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
EXTERNAL = ("http://", "https://", "mailto:", "tel:", "data:")
BANNED_MODULES = {
    "subprocess": "shell-out",
    "platform": "operating-system branch",
    "socket": "network",
    "http": "network",
    "ftplib": "network",
    "smtplib": "network",
    "requests": "network",
    "urllib.request": "network",
}
BANNED_CALLS = {"os.system": "shell-out", "os.popen": "shell-out", "sys.platform": "operating-system branch"}
NETWORK_ALLOWED: set[str] = set()
BRAND = re.compile(r"trellace", re.IGNORECASE)
BRAND_OK = re.compile(
    r"github\.com/TrellaceTeam/[a-z0-9-]+"
    r"|https://www\.trellace\.com/contact\?utm_source=github&utm_medium=skill&utm_campaign=sales-game-tape\)? with Trellace"
)


class FrontmatterError(ValueError):
    pass


def unquote_scalar(raw: str) -> str:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    if value[:1] in {"|", ">"}:
        raise FrontmatterError("block scalars (| or >) are not portable, use a single-line value")
    if ": " in value or value.endswith(":") or value[:1] in {"[", "{", "&", "*", "!", "%", "@", "`", "#"}:
        raise FrontmatterError(f"quote this value, it isn't plain YAML: {value[:60]}")
    return value


def parse_frontmatter(text: str) -> tuple[dict, int]:
    """Parse the small YAML subset skills use. Return (data, line index after frontmatter)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise FrontmatterError("SKILL.md must start with --- frontmatter")
    data: dict = {}
    current_map: dict | None = None
    for index in range(1, len(lines)):
        line = lines[index]
        if line.strip() == "---":
            return data, index + 1
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")):
            if current_map is None:
                raise FrontmatterError(f"unexpected indented line: {line.strip()[:60]}")
            key, sep, value = line.strip().partition(":")
            if not sep:
                raise FrontmatterError(f"expected key: value under a map: {line.strip()[:60]}")
            current_map[key.strip()] = unquote_scalar(value)
            continue
        key, sep, value = line.partition(":")
        if not sep:
            raise FrontmatterError(f"expected key: value: {line.strip()[:60]}")
        key = key.strip()
        if key in data:
            raise FrontmatterError(f"duplicate key: {key}")
        if value.strip():
            data[key] = unquote_scalar(value)
            current_map = None
        else:
            current_map = {}
            data[key] = current_map
    raise FrontmatterError("frontmatter has no closing ---")


def slug(heading: str) -> str:
    text = re.sub(r"`([^`]*)`", r"\1", heading)
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = unicodedata.normalize("NFKC", text).lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def anchors_in(path: Path) -> set[str]:
    found: set[str] = set()
    counts: dict[str, int] = {}
    in_fence = False
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = HEADING.match(line)
        if match:
            base = slug(match.group(2))
            n = counts.get(base, 0)
            found.add(base if n == 0 else f"{base}-{n}")
            counts[base] = n + 1
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
        links.extend((number, target) for target in INLINE_LINK.findall(stripped))
    return links


def check_links(folder: Path) -> list[str]:
    problems = []
    root = folder.resolve()
    for md in sorted(folder.rglob("*.md")):
        rel = md.relative_to(folder).as_posix()
        for number, target in links_in(md):
            if target.startswith(EXTERNAL):
                continue
            target_path, _, anchor = target.partition("#")
            target_path = unquote(target_path.split("?", 1)[0])
            resolved = (md.parent / target_path).resolve() if target_path else md.resolve()
            if root != resolved and root not in resolved.parents:
                problems.append(f"{rel}:{number}: link leaves the skill folder, so it breaks when the skill is installed alone: {target}")
                continue
            if not resolved.exists():
                problems.append(f"{rel}:{number}: missing file: {target}")
                continue
            if anchor and resolved.suffix == ".md" and anchor not in anchors_in(resolved):
                problems.append(f"{rel}:{number}: missing anchor: {target}")
    return problems


def check_script(path: Path, folder: Path) -> list[str]:
    rel = path.relative_to(folder).as_posix()
    try:
        tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    except SyntaxError as error:
        return [f"{rel}: does not parse: {error}"]
    # sys.stdlib_module_names exists from Python 3.10. On older versions this check is skipped.
    stdlib = set(getattr(sys, "stdlib_module_names", ()))
    stdlib |= {"__future__"} if stdlib else set()
    local = {p.stem for p in path.parent.glob("*.py")}
    problems = []
    for node in ast.walk(tree):
        modules = []
        if isinstance(node, ast.Import):
            modules = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            modules = [node.module] + [f"{node.module}.{alias.name}" for alias in node.names]
        for module in modules:
            top = module.split(".")[0]
            for banned, why in BANNED_MODULES.items():
                if why == "network" and path.name in NETWORK_ALLOWED:
                    continue
                if module == banned or module.startswith(banned + "."):
                    problems.append(f"{rel}:{node.lineno}: imports {module} ({why}), which portable scripts leave out")
            if stdlib and top not in stdlib and top not in local:
                problems.append(f"{rel}:{node.lineno}: imports {module}, which is not in the Python standard library")
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            dotted = f"{node.value.id}.{node.attr}"
            if dotted in BANNED_CALLS:
                problems.append(f"{rel}:{node.lineno}: uses {dotted} ({BANNED_CALLS[dotted]}), which portable scripts leave out")
    return sorted(set(problems))


def check_skill(folder: Path) -> list[str]:
    """Return a list of problems for one skill folder. An empty list means it passes."""
    folder = Path(folder)
    problems: list[str] = []
    skill_md = folder / "SKILL.md"
    if not skill_md.is_file():
        return ["SKILL.md is missing at the folder root"]
    nested = [p for p in folder.rglob("SKILL.md") if p != skill_md]
    for extra in nested:
        problems.append(f"{extra.relative_to(folder).as_posix()}: a second SKILL.md indexes as its own skill, rename it")

    text = skill_md.read_text(encoding="utf-8-sig")
    try:
        data, body_start = parse_frontmatter(text)
    except FrontmatterError as error:
        return problems + [f"SKILL.md: frontmatter: {error}"]

    for key in sorted(set(data) - ALLOWED_KEYS):
        problems.append(f"SKILL.md: frontmatter key '{key}' is not portable, keep only {', '.join(sorted(ALLOWED_KEYS))}")

    name = data.get("name")
    if not isinstance(name, str) or not name:
        problems.append("SKILL.md: frontmatter needs a name")
    else:
        if not NAME.match(name) or len(name) > 64:
            problems.append(f"SKILL.md: name '{name}' must be lowercase letters, numbers and single hyphens, 1 to 64 characters")
        if name != folder.resolve().name:
            problems.append(f"SKILL.md: name '{name}' must equal the folder name '{folder.resolve().name}'")

    description = data.get("description")
    if not isinstance(description, str) or not description.strip():
        problems.append("SKILL.md: frontmatter needs a description")
    elif len(description) > MAX_DESCRIPTION:
        problems.append(f"SKILL.md: description is {len(description)} characters, keep it under 200")

    if "license" in data and not isinstance(data["license"], str):
        problems.append("SKILL.md: license must be a single string")
    if "metadata" in data:
        metadata = data["metadata"]
        if not isinstance(metadata, dict) or not all(isinstance(v, str) for v in metadata.values()):
            problems.append("SKILL.md: metadata must be a map of strings to strings")

    body = text.splitlines()[body_start:]
    first = next((line for line in body if line.strip()), "")
    if not first.startswith("# "):
        problems.append("SKILL.md: put a one-line H1 with the skill's name right after the frontmatter")
    if len(text.splitlines()) > MAX_LINES:
        problems.append(f"SKILL.md: {len(text.splitlines())} lines, move reference material to references/ to stay under {MAX_LINES}")

    problems.extend(check_links(folder))
    for script in sorted(folder.rglob("*.py")):
        problems.extend(check_script(script, folder))
    for doc in sorted(folder.rglob("*")):
        if doc.is_file() and doc.suffix in {".md", ".py", ".txt"}:
            for number, line in enumerate(doc.read_text(encoding="utf-8-sig").splitlines(), start=1):
                if BRAND.search(BRAND_OK.sub("", line)):
                    problems.append(f"{doc.relative_to(folder).as_posix()}:{number}: brand name outside a "
                                    "github.com/TrellaceTeam link or the closing line")
    return problems


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="*", help="Skill folders to check.")
    parser.add_argument("--all", dest="root", help="Check every folder under this one that holds a SKILL.md.")
    args = parser.parse_args(argv)

    folders = [Path(p) for p in args.paths]
    if args.root:
        folders += sorted(p.parent for p in Path(args.root).glob("*/SKILL.md"))
    if not folders:
        parser.error("name at least one skill folder, or use --all")

    failed = 0
    for folder in folders:
        problems = check_skill(folder)
        label = folder.as_posix()
        if problems:
            failed += 1
            for problem in problems:
                print(f"{label}/{problem}")
        else:
            print(f"{label}: ok")
    print(f"check_skill: {len(folders)} checked, {failed} with problems")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
