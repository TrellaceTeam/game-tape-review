#!/usr/bin/env python3
"""Game tape helper: convert call transcripts, show a clip, check a run sheet.

Usage:
    python tape.py convert FILE [FILE ...] [--out FILE | --out-dir DIR] [header options]
    python tape.py link COPIED_LINK TIME
    python tape.py window TRANSCRIPT START END [--quote "exact words"]... [--quotes FILE]
    python tape.py check RUN_SHEET TRANSCRIPTS_FOLDER

convert reads a transcript export and writes it in the game-tape format. It reads
WebVTT (.vtt), SubRip (.srt), Word (.docx), JSON from a recorder's API, and the
common text layouts, such as "[00:01:23] Name: text", "00:01:23 Name: text",
"Name (00:01:23): text", and a "Name  1:23" line with the words on the lines
below it. Header options: --title, --date, --rep, --call-type, --link, --buyers,
--name "Speaker 1=Jordan Ellis" to rename a speaker, and --zero to count times from
the first line when an export shows the time of day. It never changes a word.
In subtitle and JSON files, back-to-back pieces from one speaker join into one
line of up to about 20 seconds.

link reads one link copied from a recorder's "copy link at this time" button, and
the time the player showed, and prints the LINK template with the time swapped
for a placeholder.

window prints the transcript lines between START and END, the link that opens at
START, and marks each quote FOUND or MISSING.

check reads a finished run sheet and checks it against the transcripts. Every
quote written as "[HH:MM:SS] exact words" has to sit on that transcript line.
Every link whose label holds a time, such as [4:40 to 6:49](...), has to match a
transcript's LINK, open at the label's first time, and cover transcript lines.

The game-tape format is a few header lines, a blank line, then one line per turn:

    TITLE: First call with Ashgrove Plastics
    DATE: 2026-09-22
    MINUTES: 27
    REP: Jordan Ellis
    CALL_TYPE: first call
    LINK: https://recorder.example/share/abc?t={seconds}
    BUYERS: Dana Whitfield, VP of Operations

    [00:00:13] Jordan Ellis: Hi Dana, thanks for making the time.

In LINK, a placeholder marks where the recorder takes a start time: {seconds} for
whole seconds, {ms} for milliseconds, {time} for the 1m25s form, and {end} for an
end second where a recorder takes one.

Python 3.9 or later, standard library only. Reads and writes local files only.
Exit code 0 when everything passes, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote_plus, urlsplit
from xml.etree import ElementTree

HEADER_KEYS = ["TITLE", "DATE", "MINUTES", "REP", "CALL_TYPE", "LINK", "BUYERS"]
JOIN_SECONDS = 20
STAMP = r"\d{1,2}:\d{2}(?::\d{2})?(?:[.,]\d{1,3})?"
TAPE_LINE = re.compile(r"^\[(\d{1,2}:\d{2}:\d{2})\]\s*(.*)$")
CUE_TIME = re.compile(rf"^\s*({STAMP})\s*-->\s*({STAMP})")
TIME_ONLY = re.compile(rf"^\s*[\[(]?({STAMP})[\])]?\s*$")
NAME = re.compile(r"^[^\W\d_][\w .'&@()/-]{0,58}$")
MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
URL = re.compile(r"https?://[^\s<>\"')\]]+")
ISO_TIME = re.compile(r"(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2}):(\d{2})(?:[.,](\d+))?\s*(Z|[+-]\d{2}:?\d{2})?$")
PARTICLES = {"de", "van", "von", "da", "di", "la", "le", "del", "der", "den", "du", "bin", "al", "el", "of", "and"}
GENERIC_NAME = re.compile(r"(unknown speaker|unknown|speaker|spk|guest|participant)[ _-]?\w{0,3}|\d+", re.I)
PLACEHOLDERS = {
    "{seconds}": r"(?P<seconds>\d+)",
    "{ms}": r"(?P<ms>\d+)",
    "{time}": r"(?P<time>(?:\d+h)?(?:\d+m)?\d+s)",
    "{end}": r"(?P<end>\d+)",
}

# Layouts with the time, the speaker and the words on one line.
SINGLE_LINE_LAYOUTS = [
    ("[time] name: text", re.compile(rf"^\[({STAMP})(?:\s*-\s*{STAMP})?\]\s*(?:[-|]\s*)?(?P<name>[^:]{{1,60}}?):\s+(?P<text>.+)$")),
    ("time name: text", re.compile(rf"^\(?({STAMP})\)?\s*(?:[-|]\s*)?(?P<name>[^:\d][^:]{{0,59}}?):\s+(?P<text>.+)$")),
    ("name (time): text", re.compile(rf"^(?P<name>[^:\[\]()\d][^:\[\]()]{{0,59}}?)\s*[\[(]({STAMP})[\])]\s*[:-]?\s+(?P<text>.+)$")),
]
# Layouts with the time and the speaker on one line and the words on the lines below.
HEADER_LAYOUTS = [
    ("name time, then text", re.compile(rf"^(?P<name>[^\d\s][^\t]{{0,59}}?)\s*(?:[-|,]\s*|\s)\s*[\[(]?({STAMP})[\])]?\s*$")),
    ("time name, then text", re.compile(rf"^[\[(]?({STAMP})[\])]?\s*(?:[-|,]\s*|\s)\s*(?P<name>[^\d\s][^\t:]{{0,59}}?)\s*:?\s*$")),
]

TEXT_KEYS = ("text", "sentence", "content", "words", "transcript", "raw_text", "utterance", "snippet",
             "spokenText")
SPEAKER_KEYS = ("speaker_name", "speakerName", "speaker", "display_name", "displayName", "name",
                "participant", "participant_name", "participantName", "speaker_label", "speakerLabel",
                "speakerId", "speaker_id", "user")
TIME_KEYS = ("start_time", "startTime", "start", "timestamp", "start_timestamp", "startTimestamp",
             "start_offset", "startOffset", "offset", "start_ms", "startMs", "start_time_ms", "snippet_time",
             "startDateTime", "timestamps", "time", "begin")
EPOCH_SECONDS = 1_000_000_000


# ---------- small helpers ----------

def to_seconds(stamp: str) -> int:
    """'1:02:03', '02:03', '00:02:03.500' or '[02:03]' to whole seconds."""
    clean = re.split(r"[.,]", stamp.strip().strip("[]()"))[0]
    parts = [int(p) for p in clean.split(":")]
    if len(parts) == 2:
        parts = [0] + parts
    if len(parts) != 3:
        raise ValueError(f"not a time: {stamp}")
    hours, minutes, seconds = parts
    return hours * 3600 + minutes * 60 + seconds


def hms(seconds: int) -> str:
    hours, rest = divmod(int(seconds), 3600)
    minutes, secs = divmod(rest, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def short(seconds: int) -> str:
    hours, rest = divmod(int(seconds), 3600)
    minutes, secs = divmod(rest, 60)
    return f"{hours}:{minutes:02d}:{secs:02d}" if hours else f"{minutes}:{secs:02d}"


def squash(text: str) -> str:
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", text).strip().lower()


def one_line(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def name_like(value: str) -> bool:
    value = value.strip()
    return bool(NAME.match(value)) and len(value.split()) <= 6 and not value.endswith((".", "?", "!", ","))


def proper_name(value: str) -> bool:
    """'Karen Holt' or 'Speaker 2' look like a speaker. 'Let's meet at' looks like speech."""
    words = value.replace("(", " ").replace(")", " ").split()
    return bool(words) and all(w[0].isupper() or w[0].isdigit() or w.lower() in PARTICLES for w in words)


def iso_seconds(text: str):
    """An ISO date and time to epoch seconds, on any Python from 3.9, or None."""
    match = ISO_TIME.match(text.strip())
    if not match:
        return None
    year, month, day, hour, minute, second, fraction, zone = match.groups()
    moment = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second), tzinfo=timezone.utc)
    seconds = moment.timestamp() + (float("0." + fraction) if fraction else 0.0)
    if zone and zone != "Z":
        sign = 1 if zone[0] == "+" else -1
        digits = zone[1:].replace(":", "")
        seconds -= sign * (int(digits[:2]) * 3600 + int(digits[2:4] or 0) * 60)
    return seconds


def find_date(text: str) -> str:
    iso = re.search(r"\b(20\d{2})[-/](\d{2})[-/](\d{2})\b", text)
    if iso:
        return f"{iso.group(1)}-{iso.group(2)}-{iso.group(3)}"
    named = re.search(r"\b([A-Za-z]{3,9})\.? (\d{1,2}),? (20\d{2})\b", text)
    if named and named.group(1).lower()[:3] in MONTHS:
        month = MONTHS.index(named.group(1).lower()[:3]) + 1
        return f"{named.group(3)}-{month:02d}-{int(named.group(2)):02d}"
    return ""


# ---------- readers ----------

class Transcript:
    def __init__(self, turns, header=None, layout="", rough=False, preamble=None, notes=None):
        self.turns = turns            # list of (seconds, speaker, text)
        self.header = header or {}
        self.layout = layout
        self.rough = rough
        self.preamble = preamble or []
        self.notes = notes or []      # things a person should check, such as a speaker seen once


def read_tape(path: Path) -> Transcript:
    """Read a file already in the game-tape format."""
    header, turns = {}, []
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        match = TAPE_LINE.match(raw)
        if match:
            stamp, rest = match.groups()
            speaker, _, spoken = rest.partition(": ")
            if not spoken:
                speaker, spoken = "", rest
            turns.append((to_seconds(stamp), speaker.strip(), spoken.strip()))
        elif ":" in raw and not turns:
            key, value = raw.split(":", 1)
            if key.strip().upper() in HEADER_KEYS:
                header[key.strip().upper()] = value.strip()
    return Transcript(turns, header, "game tape")


def _is_tape(text: str) -> bool:
    lines = [l for l in text.splitlines() if l.strip()]
    keys = sum(1 for l in lines[:10] if l.split(":", 1)[0].strip().upper() in HEADER_KEYS)
    return keys >= 2 and any(TAPE_LINE.match(l) for l in lines)


def read_cues(text: str) -> Transcript:
    """WebVTT or SubRip. Speakers come from <v Name> tags or a 'Name: ' prefix."""
    turns, voice = [], re.compile(r"<v(?:\.[\w.]+)?\s+([^>]+)>")
    for block in re.split(r"\n\s*\n", text.replace("\r\n", "\n")):
        lines = [l for l in block.split("\n") if l.strip()]
        for index, line in enumerate(lines):
            match = CUE_TIME.match(line)
            if not match:
                continue
            body = " ".join(lines[index + 1:])
            found = voice.search(body)
            speaker = found.group(1).strip() if found else ""
            body = one_line(re.sub(r"<[^>]+>", "", body))
            prefix = ""
            if not speaker:
                name, sep, rest = body.partition(": ")
                if sep and name_like(name):
                    speaker, prefix, body = name.strip(), f"{name}: ", rest
            if body:
                turns.append([to_seconds(match.group(1)), speaker, body, prefix + body, bool(found)])
            break
    notes = []
    turns = _fold_rare_speakers(turns, notes)
    return Transcript(_join(turns), layout="subtitles (VTT or SRT)", notes=notes)


def read_json(text: str) -> Transcript:
    data = json.loads(text)
    best = []
    for items in _lists_of_dicts(data):
        found = _turns_from_items(items, "")
        if len(found) > len(best):
            best = found
    if not best:
        raise ValueError("no list of transcript lines with a text field in this JSON")
    return Transcript(_join(_normalize_times(best)), layout="JSON")


def _lists_of_dicts(node):
    if isinstance(node, list):
        if node and sum(isinstance(i, dict) for i in node) >= len(node) / 2:
            yield node
        for item in node:
            yield from _lists_of_dicts(item)
    elif isinstance(node, dict):
        for value in node.values():
            yield from _lists_of_dicts(value)


def _pick(item: dict, keys):
    for key in keys:
        if key in item and item[key] not in (None, ""):
            return key, item[key]
    return None, None


def _turns_from_items(items, inherited):
    turns = []
    for item in items:
        if not isinstance(item, dict):
            continue
        _, speaker = _pick(item, SPEAKER_KEYS)
        if isinstance(speaker, dict):
            _, speaker = _pick(speaker, ("display_name", "displayName", "name", "email", "id"))
        speaker = str(speaker) if speaker not in (None, "") else inherited
        _, text = _pick(item, TEXT_KEYS)
        if isinstance(text, str) and text.strip():
            time_key, start = _pick(item, TIME_KEYS)
            if isinstance(start, list):
                start = start[0] if start else None
            turns.append((start, time_key or "", speaker, one_line(text)))
            continue
        for value in item.values():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                turns.extend(_turns_from_items(value, speaker))
    return turns


def _normalize_times(raw):
    """Turn raw start values (seconds, ms, 'HH:MM:SS' or ISO times) into seconds from the start."""
    values = []
    for start, key, _, _ in raw:
        if isinstance(start, bool):
            values.append(("none", None))
        elif isinstance(start, (int, float)):
            values.append(("number", float(start)))
        elif isinstance(start, str) and re.fullmatch(STAMP, start.strip()):
            values.append(("stamp", float(to_seconds(start))))
        elif isinstance(start, str) and re.fullmatch(r"\d+(\.\d+)?", start.strip()):
            values.append(("number", float(start)))
        elif isinstance(start, str) and iso_seconds(start) is not None:
            values.append(("iso", iso_seconds(start)))
        else:
            values.append(("none", None))
    if all(kind == "none" for kind, _ in values):
        raise ValueError("no start times found in this JSON, so clips can't be timed")
    numbers = [v for kind, v in values if kind == "number"]
    keys = {key.lower() for _, key, _, _ in raw}
    in_ms = any("ms" in key or "milli" in key for key in keys) or bool(numbers and max(numbers) > 36000)
    offset = 0
    if numbers:
        scaled = [n / 1000 if in_ms else n for n in numbers]
        # Clock times, such as epoch milliseconds, count from the first line.
        offset = min(scaled) if min(scaled) > EPOCH_SECONDS else 0
    first_iso = min((v for kind, v in values if kind == "iso"), default=0)
    turns, last = [], 0
    for (kind, value), (_, _, speaker, text) in zip(values, raw):
        if kind == "number":
            last = int((value / 1000 if in_ms else value) - offset)
        elif kind == "stamp":
            last = int(value)
        elif kind == "iso":
            last = int(value - first_iso)
        turns.append((max(0, last), speaker, text))
    return turns


def read_docx(path: Path) -> str:
    ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    with zipfile.ZipFile(path) as archive:
        root = ElementTree.fromstring(archive.read("word/document.xml"))
    paragraphs = []
    for para in root.iter(f"{ns}p"):
        pieces = []
        for node in para.iter():
            if node.tag == f"{ns}t" and node.text:
                pieces.append(node.text)
            elif node.tag == f"{ns}tab":
                pieces.append("\t")
            elif node.tag in (f"{ns}br", f"{ns}cr"):
                pieces.append("\n")
        paragraphs.append("".join(pieces))
    return "\n".join(paragraphs)


def read_text(text: str) -> Transcript:
    lines = _merge_split_headers([l.rstrip() for l in text.replace("\r\n", "\n").split("\n")])
    if not any(l.strip() for l in lines):
        raise ValueError("the file is empty")
    tries = [_parse_lines(lines, label, pattern, False) for label, pattern in SINGLE_LINE_LAYOUTS]
    tries += [_parse_lines(lines, label, pattern, True) for label, pattern in HEADER_LAYOUTS]
    starts, label, turns, first = max(tries, key=lambda t: t[0])
    if starts >= 2:
        preamble = [l.strip() for l in lines[:first] if l.strip()]
        notes = []
        turns = _fold_rare_speakers(turns, notes)
        return Transcript(turns, layout=f"text ({label})", preamble=preamble, notes=notes)
    rough = _read_rough(lines)
    if rough:
        return rough
    raise ValueError("found no timestamps with speaker names. Export the transcript with timestamps "
                     "and speakers turned on, or as .vtt, .srt or .docx")


def _parse_lines(lines, label, pattern, words_below):
    """Return (turn starts found, label, turns, index of the first turn line)."""
    turns, first = [], None
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        match = pattern.match(stripped)
        if match and name_like(match.group("name")):
            stamp = next(g for g in match.groups() if g and re.fullmatch(STAMP, g))
            spoken = "" if words_below else match.group("text").strip()
            turns.append([to_seconds(stamp), match.group("name").strip(), spoken, stripped])
            first = index if first is None else first
        elif turns:
            turns[-1][2] = f"{turns[-1][2]} {stripped}".strip()
            turns[-1][3] = f"{turns[-1][3]} {stripped}"
    if words_below:
        # A "header" with no words under it was most likely a line of speech that ends in a time.
        kept = []
        for turn in turns:
            if not turn[2] and kept:
                kept[-1][2] = f"{kept[-1][2]} {turn[3]}"
                kept[-1][3] = f"{kept[-1][3]} {turn[3]}"
            elif turn[2]:
                kept.append(turn)
        turns = kept
    return len(turns), label, turns, first


def _merge_split_headers(lines):
    """Join a name line and a time-only line under it, as in 'Dana Whitfield' then '00:02:18'."""
    merged, skip = [], False
    for index, line in enumerate(lines):
        if skip:
            skip = False
            continue
        following = lines[index + 1] if index + 1 < len(lines) else ""
        only = TIME_ONLY.match(following)
        if line.strip() and name_like(line) and only:
            merged.append(f"{line.strip()}  {only.group(1)}")
            skip = True
        else:
            merged.append(line)
    return merged


def _fold_rare_speakers(turns, notes):
    """A "speaker" seen once whose name reads like speech, such as "Let's meet at", is more likely
    words that matched the layout. Put that whole line back into the turn before it, so no word is
    lost. A speaker seen once who looks like a person, such as a buyer's boss, stays, with a note.
    Speakers from voice tags always stay."""
    counts = {}
    for turn in turns:
        counts[turn[1]] = counts.get(turn[1], 0) + 1
    kept = []
    for turn in turns:
        rare = len(turns) >= 6 and turn[1] and counts[turn[1]] < 2
        tagged = len(turn) > 4 and turn[4]
        if rare and not tagged and not proper_name(turn[1]) and kept:
            kept[-1][2] = f"{kept[-1][2]} {turn[3]}"
            kept[-1][3] = f"{kept[-1][3]} {turn[3]}"
            continue
        if rare:
            notes.append(f"{turn[1]} speaks only once, at {short(turn[0])}. Check that's a real speaker.")
        kept.append(turn)
    return [(t[0], t[1], one_line(t[2])) for t in kept]


def _read_rough(lines):
    """'Name: text' paragraphs with a time line every few minutes, as in some meeting-doc transcripts."""
    turns, last, seen_time, preamble = [], 0, False, []
    for line in lines:
        only = TIME_ONLY.match(line)
        if only:
            last, seen_time = to_seconds(only.group(1)), True
            continue
        speaker, sep, spoken = line.strip().partition(": ")
        if sep and name_like(speaker) and spoken:
            turns.append([last, speaker.strip(), spoken.strip(), line.strip()])
        elif turns and line.strip():
            turns[-1][2] += " " + line.strip()
            turns[-1][3] += " " + line.strip()
        elif line.strip():
            preamble.append(line.strip())
    if seen_time and len(turns) >= 2:
        notes = []
        turns = _fold_rare_speakers(turns, notes)
        return Transcript(turns, layout="text with times every few minutes", rough=True, preamble=preamble, notes=notes)
    return None


def _join(turns):
    """Join back-to-back pieces from one speaker into lines of up to about JOIN_SECONDS."""
    joined = []
    for seconds, speaker, text in turns:
        if joined and joined[-1][1] == speaker and seconds - joined[-1][0] <= JOIN_SECONDS:
            start, _, previous = joined[-1]
            joined[-1] = (start, speaker, f"{previous} {text}")
        else:
            joined.append((seconds, speaker, text))
    return joined


def load_any(path: Path, names: dict) -> Transcript:
    suffix = path.suffix.lower()
    if suffix == ".docx":
        result = read_text(read_docx(path))
        result.layout = "Word, " + result.layout
    else:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        result = None
        if suffix == ".json" or text.lstrip()[:1] in ("{", "["):
            try:
                result = read_json(text)
            except json.JSONDecodeError:
                if suffix == ".json":
                    raise
        if result is None:
            if suffix in (".vtt", ".srt") or text.lstrip().startswith("WEBVTT") or re.search(rf"^\s*{STAMP}\s*-->", text, re.M):
                result = read_cues(text)
            elif _is_tape(text):
                result = read_tape(path)
            else:
                result = read_text(text)
    if not result.turns:
        raise ValueError("found no transcript lines")
    if names:
        result.turns = [(s, names.get(sp, sp), t) for s, sp, t in result.turns]
    return result


# ---------- convert ----------

def render(result: Transcript, values: dict, source: Path) -> str:
    header = {key: result.header.get(key, "") for key in HEADER_KEYS}
    if not header["TITLE"]:
        header["TITLE"] = result.preamble[0] if result.preamble else source.stem.replace("_", " ")
    if not header["DATE"]:
        header["DATE"] = next((d for d in map(find_date, result.preamble) if d), "") or find_date(source.stem)
    header["MINUTES"] = header["MINUTES"] or str(max(1, round(result.turns[-1][0] / 60)))
    if not header["LINK"]:
        header["LINK"] = next((m.group(0) for m in map(URL.search, result.preamble) if m), "")
    for key, value in values.items():
        if value is not None:
            header[key] = value
    lines = [f"{key}: {header[key]}" for key in HEADER_KEYS]
    if result.rough:
        lines.append("TIMES: rough, the export marks the time only every few minutes")
    lines.append("")
    lines += [f"[{hms(s)}] {sp or 'Unknown'}: {t}" for s, sp, t in result.turns]
    return "\n".join(lines) + "\n"


def convert(args) -> int:
    if args.out and len(args.files) > 1:
        print("Use --out-dir with more than one file.", file=sys.stderr)
        return 1
    names = {}
    for pair in args.name:
        old, sep, new = pair.partition("=")
        if not sep:
            print(f"--name needs OLD=NEW, got {pair!r}", file=sys.stderr)
            return 1
        names[old.strip()] = new.strip()
    values = {"TITLE": args.title, "DATE": args.date, "REP": args.rep, "CALL_TYPE": args.call_type,
              "LINK": args.link, "BUYERS": args.buyers}
    failed = 0
    for name in args.files:
        source = Path(name)
        try:
            result = load_any(source, names)
        except (ValueError, OSError, KeyError, zipfile.BadZipFile, ElementTree.ParseError) as error:
            print(f"{source}: {error}", file=sys.stderr)
            failed += 1
            continue
        first = result.turns[0][0]
        if args.zero and first:
            result.turns = [(s - first, sp, t) for s, sp, t in result.turns]
        text = render(result, values, source)
        target = Path(args.out) if args.out else (Path(args.out_dir) / f"{source.stem}.txt" if args.out_dir else None)
        if target and target.resolve() == source.resolve():
            target = target.with_name(f"{source.stem}.tape.txt")
        speakers = list(dict.fromkeys(sp or "Unknown" for _, sp, _ in result.turns))
        note = (f"{len(result.turns)} lines, {len(speakers)} speakers ({', '.join(speakers[:6])}), "
                f"{short(result.turns[-1][0])} long, read as {result.layout}")
        say = print if target else (lambda message: print(message, file=sys.stderr))
        if target:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
            say(f"wrote {target}: {note}")
        else:
            sys.stdout.write(text)
            say(note)
        if len(speakers) < 2:
            say("  check: only one speaker found. Check that the export has speaker names.")
        if any(GENERIC_NAME.fullmatch(s) for s in speakers):
            say('  check: some speaker names are generic. Rename them with --name "Speaker 1=Full Name".')
        if result.rough:
            say("  check: times appear only every few minutes, so clip links will be rough.")
        if not args.zero and first >= 3600:
            say(f"  check: the first line is at {short(first)}, which looks like a time of day. "
                "If the recording starts at the first line, run again with --zero.")
        for item in result.notes:
            say(f"  check: {item}")
    return 1 if failed else 0


# ---------- window ----------

def time_text(seconds: int) -> str:
    """85 as '1m25s', the form some players take."""
    hours, rest = divmod(int(seconds), 3600)
    minutes, secs = divmod(rest, 60)
    return (f"{hours}h" if hours else "") + (f"{minutes}m" if hours or minutes else "") + f"{secs}s"


def link_at(template: str, seconds: int, end: int = 0) -> str:
    if not template:
        return ""
    if not any(mark in template for mark in PLACEHOLDERS):
        return f"{template}  (no start-time link, open at {short(seconds)})"
    values = {"{seconds}": str(seconds), "{ms}": str(seconds * 1000), "{time}": time_text(seconds),
              "{end}": str(end or seconds + 180)}
    for mark, value in values.items():
        template = template.replace(mark, value)
    return template


def _spans(quote: str, spoken: str):
    """Where each piece of the quote, split at '...', sits in the line, in order, or None."""
    pieces = [p for p in (squash(x).strip(" ") for x in re.split(r"\.\.\.|…", quote)) if p]
    if not pieces:
        return None
    haystack, position, spans = squash(spoken), 0, []
    for piece in pieces:
        found = haystack.find(piece, position)
        if found < 0:
            return None
        spans.append((found, found + len(piece)))
        position = found + len(piece)
    return haystack, spans


def find_quote(quote: str, spoken: str) -> bool:
    """Every piece of the quote, split at '...', appears in the line in order. Case and spacing don't count."""
    return _spans(quote, spoken) is not None


CUT_WORDS = re.compile(r"\b(not|never|no)\b|n't\b|\d")
NEXT_TO = re.compile(r"^(not|never)$|n't$")


def cut_problem(quote: str, spoken: str) -> str:
    """A cut that can flip the meaning: a 'not' or a number inside a '...', or a 'not' right before or after."""
    found = _spans(quote, spoken)
    if not found:
        return ""
    haystack, spans = found
    for (_, end), (start, _) in zip(spans, spans[1:]):
        gap = haystack[end:start]
        if CUT_WORDS.search(gap):
            return f"the '...' cuts \"{gap.strip()[:60]}\", which holds a 'not' or a number"
    before = haystack[:spans[0][0]].split()[-1:]
    after = haystack[spans[-1][1]:].split()[:1]
    for word in before + after:
        if NEXT_TO.search(word.strip(".,!?;:'\"")):
            return f"it leaves out \"{word}\" right beside it, which changes what was said"
    return ""


def window(args) -> int:
    result = read_tape(Path(args.transcript))
    start, end = to_seconds(args.start), to_seconds(args.end)
    quotes = list(args.quote)
    if args.quotes:
        quotes += [q.strip() for q in Path(args.quotes).read_text(encoding="utf-8").splitlines() if q.strip()]
    lines = [(s, sp, t) for s, sp, t in result.turns if start <= s <= end]
    title = result.header.get("TITLE", Path(args.transcript).name)
    print(f"{title} | {result.header.get('DATE', '')} | clip {short(start)} to {short(end)} ({end - start} s)")
    print(f"LINK: {link_at(result.header.get('LINK', ''), start, end) or 'none in header'}")
    print()
    for s, sp, t in lines:
        print(f"[{hms(s)}] {sp}: {t}")
    ok = bool(lines)
    if not lines:
        print("NO LINES in this window. Check the times.")
    if quotes:
        print()
    for quote in quotes:
        hit = next((s for s, _, t in lines if find_quote(quote, t)), None)
        if hit is not None:
            print(f"FOUND   {quote!r} at [{hms(hit)}]")
        else:
            ok = False
            print(f"MISSING {quote!r}")
    return 0 if ok else 1


# ---------- check ----------

QUOTE = re.compile(r'["“]\[(\d{1,2}:\d{2}:\d{2})\]\s+([^"“”]+?)["”]')
STAMP_IN_SHEET = re.compile(r"\[\d{1,2}:\d{2}:\d{2}\]")
MD_LINK = re.compile(r"\[([^\]]+)\]\(<?([^)\s>]+)>?\)")
LABEL_TIME = re.compile(r"(?<![\d:])(\d{1,2}:\d{2}(?::\d{2})?)(?![\d:])")


def link_pattern(template: str):
    """A regex that matches every link a LINK template makes."""
    pieces = re.split("(" + "|".join(re.escape(mark) for mark in PLACEHOLDERS) + ")", template)
    used, regex = set(), ""
    for piece in pieces:
        if piece in PLACEHOLDERS and piece not in used:
            regex += PLACEHOLDERS[piece]
            used.add(piece)
        else:
            regex += re.escape(piece)
    return re.compile("^" + regex + "$")


def link_start(found) -> int:
    """The start second a matched link opens at, or -1 when the link holds no time."""
    groups = found.groupdict()
    if groups.get("seconds"):
        return int(groups["seconds"])
    if groups.get("ms"):
        return int(groups["ms"]) // 1000
    if groups.get("time"):
        parts = re.fullmatch(r"(?:(\d+)h)?(?:(\d+)m)?(\d+)s", groups["time"]).groups()
        return int(parts[0] or 0) * 3600 + int(parts[1] or 0) * 60 + int(parts[2])
    return -1


def check(args) -> int:
    sheet_path, folder = Path(args.run_sheet), Path(args.transcripts)
    transcripts = []
    for path in sorted(folder.rglob("*.txt")):
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        if _is_tape(text):
            transcripts.append((path.relative_to(folder).as_posix(), read_tape(path)))
    if not transcripts:
        print(f"No game-tape transcripts under {folder}. Convert them first with: tape.py convert")
        return 1
    sheet = sheet_path.read_text(encoding="utf-8-sig").splitlines()
    patterns = [(link_pattern(t.header["LINK"]), name, t) for name, t in transcripts if t.header.get("LINK")]
    problems, notes, quotes, links = [], [], 0, 0

    for number, line in enumerate(sheet, start=1):
        matches = list(QUOTE.finditer(line))
        if len(STAMP_IN_SHEET.findall(line)) > len(matches):
            problems.append(f"line {number}: a [HH:MM:SS] here isn't written as \"[HH:MM:SS] exact words\", "
                            "so its quote can't be checked")
        for match in matches:
            stamp, words = match.groups()
            if line[match.end():match.end() + 1].isalnum():
                problems.append(f"line {number}: the quote at [{stamp}] has a double quote inside it. "
                                "Use single quotes inside a quote")
            quotes += 1
            seconds = to_seconds(stamp)
            hits = [spoken for _, t in transcripts for s, _, spoken in t.turns if s == seconds and find_quote(words, spoken)]
            if hits:
                reason = cut_problem(words, hits[0])
                if reason:
                    problems.append(f"line {number}: the quote at [{stamp}] matches, but {reason}")
                continue
            message = f"line {number}: quote not found at [{stamp}]: \"{words[:80]}\""
            elsewhere = [(name, s) for name, t in transcripts for s, _, spoken in t.turns if find_quote(words, spoken)]
            same_time = [(name, spoken) for name, t in transcripts for s, _, spoken in t.turns if s == seconds]
            if elsewhere:
                message += f"\n    The same words are at [{hms(elsewhere[0][1])}] in {elsewhere[0][0]}. Use that time."
            elif same_time:
                message += f"\n    The line at [{stamp}] in {same_time[0][0]} reads: \"{same_time[0][1][:120]}\""
                message += "\n    Copy the words exactly, punctuation included."
            problems.append(message)

        for label, url in MD_LINK.findall(line):
            times = LABEL_TIME.findall(label)
            if not times:
                continue
            links += 1
            if not patterns:
                continue
            match = next(((m, name, t) for pattern, name, t in patterns for m in [pattern.match(url)] if m), None)
            if not match:
                problems.append(f"line {number}: the link [{label}] matches no transcript's LINK, so it can't be checked: {url}")
                continue
            found, name, t = match
            start = to_seconds(times[0])
            opens = link_start(found)
            if opens >= 0 and opens != start:
                problems.append(f"line {number}: the link [{label}] opens at {short(opens)}, but its label says {times[0]}")
            if len(times) >= 2:
                end = to_seconds(times[1])
                if found.groupdict().get("end") and int(found.group("end")) != end:
                    problems.append(f"line {number}: the link [{label}] ends at {short(int(found.group('end')))}, "
                                    f"but its label says {times[1]}")
                if end <= start:
                    problems.append(f"line {number}: the link [{label}] ends before it starts")
                elif not any(start <= s <= end for s, _, _ in t.turns):
                    problems.append(f"line {number}: the link [{label}] covers no lines in {name}")
            elif not any(abs(s - start) <= 30 for s, _, _ in t.turns):
                problems.append(f"line {number}: the link [{label}] opens where {name} has no lines")

    if links and not patterns:
        notes.append("No transcript has a LINK header, so no link was checked. Put each picked call's "
                     "share link in its LINK header and run the check again.")
        links = 0
    for problem in problems:
        print(problem)
    for item in notes:
        print(f"Note: {item}")
    print(f"\nQuotes checked: {quotes}. Links with times checked: {links}. Problems: {len(problems)}.")
    if quotes == 0:
        print('No quotes found. Write each quote as "[HH:MM:SS] exact words" so it can be checked.')
    return 1 if problems or quotes == 0 else 0


# ---------- link ----------

def _time_mark(value: str, target: int):
    """Which placeholder a link value stands for, when it holds the target time."""
    if re.fullmatch(r"\d+", value):
        number = int(value)
        if abs(number - target) <= 2:
            return "{seconds}"
        if number >= 1000 and abs(number / 1000 - target) <= 2:
            return "{ms}"
    if re.fullmatch(r"\d+\.\d+", value) and abs(float(value) - target) <= 2:
        return "{seconds}"
    parts = re.fullmatch(r"(?:(\d+)h)?(?:(\d+)m)?(\d+)s", value)
    if parts:
        hours, minutes, seconds = (int(p or 0) for p in parts.groups())
        if abs(hours * 3600 + minutes * 60 + seconds - target) <= 2:
            return "{time}"
    return None


def learn_link(args) -> int:
    """Find where a copied 'link at this time' holds the time, and print the LINK template."""
    target = to_seconds(args.time)
    url = args.url.strip()
    parts = urlsplit(url)
    for section in (parts.query, parts.fragment):
        for segment in section.split("&"):
            key, sep, value = segment.partition("=")
            mark = _time_mark(unquote_plus(value), target) if sep else None
            if not mark:
                continue
            template = url.replace(segment, f"{key}={mark}", 1)
            print(f"Found {short(target)} in {unquote_plus(key)}={unquote_plus(value)}.")
            print(f"LINK for this call: {template}")
            print(f"For other calls from this recorder, add {key}={mark} to each call's own link the same way.")
            return 0
    print(f"Found no {short(target)} in this link, so this recorder's links may not open at a time.")
    print("Use each call's plain link. The run sheet will say where to scrub to.")
    return 1


# ---------- main ----------

def main(argv=None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    c = sub.add_parser("convert", help="convert transcript exports to the game-tape format")
    c.add_argument("files", nargs="+")
    c.add_argument("--out", help="output file, for one input")
    c.add_argument("--out-dir", help="output folder, one .txt per input")
    for option in ("title", "date", "rep", "call-type", "link", "buyers"):
        c.add_argument(f"--{option}")
    c.add_argument("--name", action="append", default=[], help='rename a speaker: "Speaker 1=Jordan Ellis"')
    c.add_argument("--zero", action="store_true", help="count times from the first line, for exports that show the time of day")

    w = sub.add_parser("window", help="show a clip's lines and check its quotes")
    w.add_argument("transcript")
    w.add_argument("start")
    w.add_argument("end")
    w.add_argument("--quote", action="append", default=[])
    w.add_argument("--quotes", help="UTF-8 file with one quote per line")

    k = sub.add_parser("check", help="check every quote and link in a run sheet")
    k.add_argument("run_sheet")
    k.add_argument("transcripts")

    n = sub.add_parser("link", help="learn a recorder's link format from one copied 'link at this time'")
    n.add_argument("url")
    n.add_argument("time", help="the time the recording showed when the link was copied, such as 12:34")

    args = parser.parse_args(argv)
    return {"convert": convert, "window": window, "check": check, "link": learn_link}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
