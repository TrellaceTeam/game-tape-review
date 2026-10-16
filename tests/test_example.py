"""The example run sheet passes the skill's own check, and every example export converts without losing a word."""

import contextlib
import io
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "game-tape-review" / "scripts"))

import tape  # noqa: E402

EXAMPLE = ROOT / "examples" / "fennick"


def quiet(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        code = tape.main(list(argv))
    return code, out.getvalue()


class Example(unittest.TestCase):
    def work_folder(self):
        folders = sorted(p for p in EXAMPLE.glob("game-tape-review-*") if p.is_dir())
        self.assertTrue(folders, "the example has no game-tape-review-<date> work folder")
        return folders[-1]

    def test_run_sheet_passes_the_check(self):
        work = self.work_folder()
        code, output = quiet("check", str(work / "run-sheet.md"), str(work / "transcripts"))
        self.assertEqual(code, 0, output)

    def test_every_export_converts_to_its_transcript_words(self):
        work = self.work_folder()
        transcripts = {p.stem: p for p in (work / "transcripts").rglob("*.txt")}
        exports = [p for p in (EXAMPLE / "calls").iterdir() if p.name != "links.txt"]
        self.assertEqual(len(exports), len(transcripts))
        words = lambda turns: re.sub(r"\s+", " ", " ".join(t for _, _, t in turns)).strip()  # noqa: E731
        expected = {words(tape.read_tape(p).turns) for p in transcripts.values()}
        with tempfile.TemporaryDirectory() as tmp:
            for export in exports:
                target = Path(tmp) / f"{export.stem}.txt"
                code, output = quiet("convert", str(export), "--out", str(target))
                self.assertEqual(code, 0, output)
                self.assertIn(words(tape.read_tape(target).turns), expected, export.name)

    def test_profile_keeps_standing_rules(self):
        profile = (EXAMPLE / "team" / "profile.md").read_text(encoding="utf-8")
        self.assertIn("Link pattern", profile)
        self.assertIn("## Played", profile)
        self.assertNotRegex(profile, r"api[_ -]?key\s*[:=]\s*\S{12,}")

    def test_playbook_copy_is_word_for_word(self):
        original = (EXAMPLE / "fennick-first-call-playbook.md").read_text(encoding="utf-8")
        source_line, _, copy = (EXAMPLE / "team" / "playbook.md").read_text(encoding="utf-8").partition("\n")
        self.assertTrue(source_line.startswith("Copied from"), source_line)
        self.assertEqual(copy.lstrip("\n"), original)


if __name__ == "__main__":
    unittest.main()
