"""Tests for skills/game-tape/scripts/tape.py. Run: python -m unittest discover -s tests -v

Every name and line is from the fictional Fennick Software world.
"""

import contextlib
import io
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "game-tape" / "scripts"))

import tape  # noqa: E402


def run(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        code = tape.main(list(argv))
    return code, out.getvalue()


class Workspace(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, name, text):
        path = self.dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def convert(self, name, text, *options):
        source = self.write(name, text) if isinstance(text, str) else text
        target = self.dir / "out" / (Path(name).stem + ".txt")
        code, output = run("convert", str(source), "--out", str(target), *options)
        self.assertEqual(code, 0, output)
        return tape.read_tape(target), target.read_text(encoding="utf-8"), output

    def turns(self, result, count=None):
        return [(s, sp, t) for s, sp, t in result.turns[:count]]


def alternating(count, first="Jordan Ellis", second="Dana Whitfield"):
    """Back-and-forth lines, so a file is long enough for the one-time-speaker rules to apply."""
    return [(i * 6, first if i % 2 == 0 else second, f"Line {i} words.") for i in range(count)]


class ConvertLayouts(Workspace):
    def test_bracket_lines_with_a_preamble(self):
        text = ("Fennick Software / Ashgrove Plastics: discovery call (fictional example, condensed)\n"
                "Tuesday, September 22, 2026, 2:00 PM Eastern\n"
                "Attendees: Jordan Ellis (Fennick Software), Dana Whitfield (Ashgrove Plastics)\n\n"
                "[00:00:13] Jordan Ellis: Hi Dana, thanks for making the time.\n"
                "[00:00:21] Dana Whitfield: Loud and clear.\n")
        result, _, _ = self.convert("call.txt", text)
        self.assertEqual(self.turns(result), [(13, "Jordan Ellis", "Hi Dana, thanks for making the time."),
                                              (21, "Dana Whitfield", "Loud and clear.")])
        self.assertEqual(result.header["DATE"], "2026-09-22")
        self.assertTrue(result.header["TITLE"].startswith("Fennick Software / Ashgrove Plastics"))

    def test_time_ranges_from_a_connector(self):
        text = "[00:05 - 00:08] Priya Raman: How's the plant?\n[00:09 - 00:15] Ruth Adeyemi: Busy, honestly.\n"
        result, _, _ = self.convert("ranges.txt", text)
        self.assertEqual(self.turns(result), [(5, "Priya Raman", "How's the plant?"), (9, "Ruth Adeyemi", "Busy, honestly.")])

    def test_vtt_with_name_prefixes_joins_one_speakers_cues(self):
        text = ("WEBVTT\n\n1\n00:00:03.120 --> 00:00:07.480\nJordan Ellis: Thanks for jumping on.\n\n"
                "2\n00:00:07.900 --> 00:00:09.000\nJordan Ellis: Did you see the recap?\n\n"
                "3\n00:00:10.010 --> 00:00:12.950\nLuis Ortega: I did. I had a question about the phones.\n\n"
                "4\n00:00:40.000 --> 00:00:42.000\nJordan Ellis: Sure, go ahead.\n")
        result, _, _ = self.convert("zoom.vtt", text)
        self.assertEqual(self.turns(result), [(3, "Jordan Ellis", "Thanks for jumping on. Did you see the recap?"),
                                              (10, "Luis Ortega", "I did. I had a question about the phones."),
                                              (40, "Jordan Ellis", "Sure, go ahead.")])

    def test_vtt_voice_tags(self):
        text = ("WEBVTT\n\n0a1b2c3d-1/12\n00:03:02.870 --> 00:03:05.570\n<v Jordan Ellis>So what changed this quarter?</v>\n\n"
                "0a1b2c3d-1/13\n00:03:06.000 --> 00:03:09.000\n<v Dana Whitfield>We lost a press for two shifts.</v>\n")
        result, _, _ = self.convert("teams.vtt", text)
        self.assertEqual(self.turns(result), [(182, "Jordan Ellis", "So what changed this quarter?"),
                                              (186, "Dana Whitfield", "We lost a press for two shifts.")])

    def test_someone_who_speaks_once_keeps_their_line(self):
        cues = [f"{i + 1}\n00:00:{s:02d}.000 --> 00:00:{s + 5:02d}.000\n<v {sp}>{t}</v>\n" for i, (s, sp, t) in enumerate(alternating(8))]
        cues.insert(5, "99\n00:00:40.000 --> 00:00:44.000\n<v Karen Holt>I sign off on anything over $25,000.</v>\n")
        result, _, output = self.convert("tagged.vtt", "WEBVTT\n\n" + "\n".join(cues))
        self.assertIn((40, "Karen Holt", "I sign off on anything over $25,000."), self.turns(result))
        self.assertIn("Karen Holt speaks only once", output)
        prefixed = [f"{i + 1}\n00:00:{s:02d}.000 --> 00:00:{s + 5:02d}.000\n{sp}: {t}\n" for i, (s, sp, t) in enumerate(alternating(8))]
        prefixed.insert(5, "99\n00:00:40.000 --> 00:00:44.000\nKaren Holt: I sign off on anything over $25,000.\n")
        result, _, _ = self.convert("prefixed.vtt", "WEBVTT\n\n" + "\n".join(prefixed))
        self.assertIn((40, "Karen Holt", "I sign off on anything over $25,000."), self.turns(result))

    def test_srt(self):
        text = ("1\n00:00:01,000 --> 00:00:04,000\nJordan Ellis: Hi Marcus.\n\n"
                "2\n00:00:05,000 --> 00:00:07,500\nMarcus Hale: Hey. I've got 20 minutes.\n")
        result, _, _ = self.convert("call.srt", text)
        self.assertEqual(self.turns(result), [(1, "Jordan Ellis", "Hi Marcus."), (5, "Marcus Hale", "Hey. I've got 20 minutes.")])

    def test_name_and_time_then_words_below(self):
        text = ("Greg Tolliver  00:00\nHey Priya. Yeah, I got you.\n\n"
                "Priya Raman  00:07\nNo problem at all.\nHow's your week going?\n\n"
                "Greg Tolliver  01:02:03\nBusy.\n")
        result, _, _ = self.convert("otter.txt", text)
        self.assertEqual(self.turns(result), [(0, "Greg Tolliver", "Hey Priya. Yeah, I got you."),
                                              (7, "Priya Raman", "No problem at all. How's your week going?"),
                                              (3723, "Greg Tolliver", "Busy.")])

    def test_time_and_name_then_words_below_with_the_link_in_the_preamble(self):
        text = ("Ashgrove working session - September 30, 2026\n"
                "VIEW RECORDING - 13 mins: https://recorder.example/share/ab12cd\n\n---\n\n"
                "0:12 - Jordan Ellis (Fennick Software)\n  Morning, Dana. Morning, Luis.\n\n"
                "0:30 - Luis Ortega\n  They're all busy.\n\n"
                "0:41 - Jordan Ellis (Fennick Software)\n  Fair enough.\n")
        result, _, _ = self.convert("copied.txt", text)
        self.assertEqual(self.turns(result, 2), [(12, "Jordan Ellis (Fennick Software)", "Morning, Dana. Morning, Luis."),
                                                 (30, "Luis Ortega", "They're all busy.")])
        self.assertEqual(result.header["LINK"], "https://recorder.example/share/ab12cd")
        self.assertEqual(result.header["DATE"], "2026-09-30")

    def test_name_then_time_on_its_own_line(self):
        text = ("Dana Whitfield\n00:02:18\nPress 7 went down in the middle of a run.\n\n"
                "Jordan Ellis\n00:02:52\nThree weeks overdue and nobody knew.\n")
        result, _, _ = self.convert("split.txt", text)
        self.assertEqual(self.turns(result), [(138, "Dana Whitfield", "Press 7 went down in the middle of a run."),
                                              (172, "Jordan Ellis", "Three weeks overdue and nobody knew.")])

    def test_name_with_time_in_brackets(self):
        text = "Dana Whitfield (00:02:18): Press 7 went down.\nJordan Ellis (00:02:52): How does that happen?\n"
        result, _, _ = self.convert("paren.txt", text)
        self.assertEqual(self.turns(result), [(138, "Dana Whitfield", "Press 7 went down."), (172, "Jordan Ellis", "How does that happen?")])

    def test_a_line_that_looks_like_a_header_keeps_its_words(self):
        blocks = [f"{sp}  00:{s:02d}\n{t}\n" for s, sp, t in alternating(8)]
        blocks.insert(3, "Let's meet at 10:30\n")
        result, raw, _ = self.convert("tricky.txt", "\n".join(blocks))
        self.assertIn("Let's meet at 10:30", raw)
        self.assertEqual({sp for _, sp, _ in result.turns}, {"Jordan Ellis", "Dana Whitfield"})

    def test_speech_that_matched_a_name_goes_back_into_its_turn(self):
        lines = [f"[00:00:{s:02d}] {sp}: {t}" for s, sp, t in alternating(8)]
        lines.insert(4, "[00:00:25] So here's the thing: the board is always a week behind.")
        result, raw, _ = self.convert("folded.txt", "\n".join(lines) + "\n")
        self.assertIn("So here's the thing: the board is always a week behind.", raw)
        self.assertNotIn("So here's the thing", {sp for _, sp, _ in result.turns})

    def test_meeting_doc_with_times_every_five_minutes(self):
        text = ("Fennick intro - 2026/09/11 15:01 CDT - Transcript\nAttendees\nJordan Ellis, Marcus Hale\nTranscript\n"
                "Jordan Ellis: Can you hear me now?\nMarcus Hale: Yes. I had the wrong headset on.\n00:05:00\n"
                "Marcus Hale: I can see your screen.\nJordan Ellis: Good, this is the weekly plan.\n")
        result, raw, output = self.convert("meet.txt", text)
        self.assertEqual(result.turns[2][:2], (300, "Marcus Hale"))
        self.assertIn("TIMES: rough", raw)
        self.assertIn("rough", output)
        self.assertEqual(result.header["DATE"], "2026-09-11")

    def test_time_of_day_gets_a_warning_and_zero_fixes_it(self):
        text = "Greg Tolliver  14:05:12\nHey Priya.\n\nPriya Raman  14:05:20\nHi Greg.\n"
        _, _, output = self.convert("clock.txt", text)
        self.assertIn("looks like a time of day", output)
        result, _, _ = self.convert("clock2.txt", text, "--zero")
        self.assertEqual(self.turns(result), [(0, "Greg Tolliver", "Hey Priya."), (8, "Priya Raman", "Hi Greg.")])

    def test_generic_names_get_a_warning(self):
        text = "[00:00:01] Unknown Speaker: Hello?\n[00:00:04] Priya Raman: Hi, it's Priya.\n"
        _, _, output = self.convert("generic.txt", text)
        self.assertIn("generic", output)

    def test_no_times_is_an_error(self):
        path = self.write("plain.txt", "Priya Raman: hello\nRuth Adeyemi: hi\n")
        code, output = run("convert", str(path), "--out", str(self.dir / "x.txt"))
        self.assertEqual(code, 1)
        self.assertIn("no timestamps", output)

    def test_word_document(self):
        ns = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
        paragraphs = ["Ruth Adeyemi  00:00", "Thanks for making the time.", "Priya Raman  00:07", "Glad to be here."]
        body = "".join(f"<w:p><w:r><w:t xml:space=\"preserve\">{p}</w:t></w:r></w:p>" for p in paragraphs)
        path = self.dir / "call.docx"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("word/document.xml", f"<w:document {ns}><w:body>{body}</w:body></w:document>")
        result, _, output = self.convert("call.docx", path)
        self.assertEqual(self.turns(result), [(0, "Ruth Adeyemi", "Thanks for making the time."), (7, "Priya Raman", "Glad to be here.")])
        self.assertIn("Word", output)


class ConvertJson(Workspace):
    def json_turns(self, data, *options):
        result, _, output = self.convert("call.json", json.dumps(data), *options)
        return self.turns(result), output

    def test_hh_mm_ss_strings_with_speaker_objects(self):
        data = {"transcript": [
            {"speaker": {"display_name": "Dana Whitfield"}, "text": "Let's look at the budget.", "timestamp": "00:05:32"},
            {"speaker": {"display_name": "Jordan Ellis"}, "text": "Sure.", "timestamp": "00:05:40"}]}
        turns, _ = self.json_turns(data)
        self.assertEqual(turns, [(332, "Dana Whitfield", "Let's look at the budget."), (340, "Jordan Ellis", "Sure.")])

    def test_decimal_seconds_join_into_lines(self):
        data = {"data": {"transcript": {"sentences": [
            {"speaker_name": "Priya Raman", "text": "What does your rollout look like?", "start_time": 312.4},
            {"speaker_name": "Priya Raman", "text": "Roughly.", "start_time": 316.0},
            {"speaker_name": "Ruth Adeyemi", "text": "Two plants.", "start_time": 318.2}]}}}
        turns, _ = self.json_turns(data)
        self.assertEqual(turns, [(312, "Priya Raman", "What does your rollout look like? Roughly."), (318, "Ruth Adeyemi", "Two plants.")])

    def test_milliseconds_nested_sentences_and_renamed_ids(self):
        data = {"callTranscripts": [{"callId": "1", "transcript": [
            {"speakerId": "6432", "topic": "Intro", "sentences": [{"start": 512400, "end": 514100, "text": "No wait."}]},
            {"speakerId": "7781", "sentences": [{"start": 515000, "end": 516200, "text": "Go on."}]}]}]}
        turns, _ = self.json_turns(data, "--name", "6432=Jordan Ellis", "--name", "7781=Dana Whitfield")
        self.assertEqual(turns, [(512, "Jordan Ellis", "No wait."), (515, "Dana Whitfield", "Go on.")])

    def test_ids_left_as_numbers_get_a_warning(self):
        data = [{"speaker_id": 0, "transcript": "Morning, Ruth.", "timestamps": [0.6, 0.9]},
                {"speaker_id": 1, "transcript": "Good, you?", "timestamps": [2.5, 2.9]}]
        turns, output = self.json_turns(data)
        self.assertEqual(turns, [(0, "0", "Morning, Ruth."), (2, "1", "Good, you?")])
        self.assertIn("generic", output)

    def test_epoch_milliseconds_count_from_the_first_line(self):
        data = {"turns": [
            {"speaker": {"name": "Priya Raman"}, "text": "Let's start.", "start_time_ms": 1733800000000},
            {"speaker": {"name": "Greg Tolliver"}, "text": "Ready.", "start_time_ms": 1733800065000}]}
        turns, _ = self.json_turns(data)
        self.assertEqual(turns, [(0, "Priya Raman", "Let's start."), (65, "Greg Tolliver", "Ready.")])

    def test_iso_times_with_any_fraction_count_from_the_first_line(self):
        data = {"transcriptEntries": [
            {"participant": "Priya Raman", "text": "Hello.", "startTime": "2026-10-14T16:05:12Z"},
            {"participant": "Greg Tolliver", "text": "Hi.", "startTime": "2026-10-14T16:06:00.5Z"},
            {"participant": "Priya Raman", "text": "Ready?", "startTime": "2026-10-14T11:07:00.1234567-05:00"}]}
        turns, _ = self.json_turns(data)
        self.assertEqual(turns, [(0, "Priya Raman", "Hello."), (48, "Greg Tolliver", "Hi."), (108, "Priya Raman", "Ready?")])

    def test_negative_times_become_zero(self):
        data = {"utterances": [
            {"speaker_name": "Jordan Ellis", "snippet": "Can you hear me?", "snippet_time": -12.5},
            {"speaker_name": "Marcus Hale", "snippet": "Yes.", "snippet_time": 41.2}]}
        turns, _ = self.json_turns(data)
        self.assertEqual(turns, [(0, "Jordan Ellis", "Can you hear me?"), (41, "Marcus Hale", "Yes.")])


class Links(Workspace):
    def test_learns_whole_seconds(self):
        code, output = run("link", "https://app.recorder.example/view/Call::abc?t=754", "12:34")
        self.assertEqual(code, 0)
        self.assertIn("https://app.recorder.example/view/Call::abc?t={seconds}", output)

    def test_learns_the_minutes_and_seconds_form(self):
        _, output = run("link", "https://drive.example/file/d/xyz/view?t=1m25s", "1:25")
        self.assertIn("view?t={time}", output)

    def test_learns_milliseconds_and_keeps_other_parameters(self):
        _, output = run("link", "https://video.example/play?id=9&startTime=754000&tab=1", "12:34")
        self.assertIn("play?id=9&startTime={ms}&tab=1", output)

    def test_learns_a_fragment(self):
        _, output = run("link", "https://video.example/v/9#t=755", "12:34")
        self.assertIn("#t={seconds}", output)

    def test_learns_a_percent_encoded_key(self):
        _, output = run("link", "https://video.example/v/9?start%5Fat=754", "12:34")
        self.assertIn("?start%5Fat={seconds}", output)

    def test_reports_a_link_without_a_time(self):
        code, output = run("link", "https://video.example/v/9?view=summary", "12:34")
        self.assertEqual(code, 1)
        self.assertIn("plain link", output)

    def test_link_at_fills_every_placeholder(self):
        self.assertEqual(tape.link_at("https://x/embedded-call?call-id=1&from={seconds}&to={end}", 280, 409),
                         "https://x/embedded-call?call-id=1&from=280&to=409")
        self.assertEqual(tape.link_at("https://x/v?t={time}", 3725), "https://x/v?t=1h2m5s")
        self.assertIn("open at 4:40", tape.link_at("https://x/v", 280))


TRANSCRIPT = """TITLE: First call with Harrow Creek Castings
DATE: 2026-10-06
MINUTES: 22
REP: Priya Raman
CALL_TYPE: first call
LINK: https://recorder.example/share/hc1?t={seconds}
BUYERS: Ruth Adeyemi, Director of Operations

[00:04:28] Ruth Adeyemi: We looked at a couple of other tools last spring.
[00:04:40] Priya Raman: Got it. So, um, who fixes it when it breaks?
[00:07:41] Ruth Adeyemi: So if Dale on second shift could see first shift's note on his phone, before he walks the floor.
[00:07:55] Priya Raman: Walk me through what Dale would do with that at eleven at night.
[00:15:23] Ruth Adeyemi: She won't sign anything the crew won't use.
[00:16:02] Ruth Adeyemi: It cost us about $38,000 last month.
"""


class CheckRunSheet(Workspace):
    def setUp(self):
        super().setUp()
        self.write("work/transcripts/priya/2026-10-06-harrow-creek.txt", TRANSCRIPT)

    def check(self, sheet):
        self.write("work/run-sheet.md", sheet)
        return run("check", str(self.dir / "work/run-sheet.md"), str(self.dir / "work/transcripts"))

    def test_a_clean_sheet_passes(self):
        code, output = self.check(
            "**Play: [7:38 to 8:30](https://recorder.example/share/hc1?t=458).**\n"
            '- She goes with it: "[00:07:55] Walk me through what Dale would do with that at eleven at night."\n'
            '- Ruth: "[00:07:41] ...could see first shift\'s note on his phone..."\n')
        self.assertEqual(code, 0, output)
        self.assertIn("Problems: 0", output)

    def test_curly_quotes_are_checked_too(self):
        code, output = self.check("“[00:15:23] She will sign anything”\n")
        self.assertEqual(code, 1)
        self.assertIn("quote not found", output)

    def test_a_double_quote_inside_a_quote(self):
        code, output = self.check('"[00:07:55] Walk me through "what Dale" would do"\n')
        self.assertEqual(code, 1)
        self.assertIn("single quotes", output)

    def test_a_cut_that_drops_a_not(self):
        code, output = self.check('"[00:15:23] She ... sign anything the crew"\n')
        self.assertEqual(code, 1)
        self.assertIn("'not' or a number", output)
        code, output = self.check('"[00:15:23] sign anything the crew"\n')
        self.assertEqual(code, 1)
        self.assertIn("right beside it", output)

    def test_a_cut_that_drops_a_number(self):
        code, output = self.check('"[00:16:02] It cost us ... last month."\n')
        self.assertEqual(code, 1)

    def test_a_quote_with_the_wrong_time_names_the_right_one(self):
        code, output = self.check('"[00:07:50] Walk me through what Dale would do with that"\n')
        self.assertEqual(code, 1)
        self.assertIn("[00:07:55]", output)

    def test_changed_punctuation_shows_the_real_line(self):
        code, output = self.check('"[00:04:40] Got it. So um, who fixes it when it breaks?"\n')
        self.assertEqual(code, 1)
        self.assertIn("Copy the words exactly", output)

    def test_a_timestamp_outside_the_quote_form(self):
        code, output = self.check('"[00:07:55] Walk me through" and later [00:15:23] she says no.\n')
        self.assertEqual(code, 1)
        self.assertIn("can't be checked", output)

    def test_a_link_that_opens_at_the_wrong_time(self):
        code, output = self.check('[7:38 to 8:30](https://recorder.example/share/hc1?t=400) "[00:07:55] Walk me through"\n')
        self.assertEqual(code, 1)
        self.assertIn("opens at 6:40", output)

    def test_a_link_that_matches_no_transcript(self):
        code, output = self.check('[7:38 to 8:30](https://other.example/x?t=458) "[00:07:55] Walk me through"\n')
        self.assertEqual(code, 1)
        self.assertIn("matches no transcript", output)

    def test_no_link_headers_leaves_links_unchecked_with_a_note(self):
        self.write("work/transcripts/priya/2026-10-06-harrow-creek.txt",
                   TRANSCRIPT.replace("https://recorder.example/share/hc1?t={seconds}", ""))
        code, output = self.check('[7:38 to 8:30](https://recorder.example/share/hc1?t=458) "[00:07:55] Walk me through"\n')
        self.assertEqual(code, 0, output)
        self.assertIn("No transcript has a LINK header", output)

    def test_a_window_with_no_lines(self):
        code, output = self.check('[1:00 to 2:00](https://recorder.example/share/hc1?t=60) "[00:07:55] Walk me through"\n')
        self.assertEqual(code, 1)
        self.assertIn("covers no lines", output)

    def test_no_quotes_fails(self):
        code, output = self.check("Nothing quoted here.\n")
        self.assertEqual(code, 1)
        self.assertIn("No quotes found", output)

    def test_start_and_end_links(self):
        self.write("work/transcripts/priya/2026-10-06-harrow-creek.txt",
                   TRANSCRIPT.replace("share/hc1?t={seconds}", "embedded-call?call-id=1&from={seconds}&to={end}"))
        good = self.check('[7:38 to 8:30](https://recorder.example/embedded-call?call-id=1&from=458&to=510) "[00:07:55] Walk me"\n')
        bad = self.check('[7:38 to 8:30](https://recorder.example/embedded-call?call-id=1&from=458&to=999) "[00:07:55] Walk me"\n')
        self.assertEqual(good[0], 0, good[1])
        self.assertIn("ends at", bad[1])


class Window(Workspace):
    def test_prints_lines_link_and_quote_marks(self):
        path = self.write("t.txt", TRANSCRIPT)
        code, output = run("window", str(path), "7:38", "8:30", "--quote", "eleven at night", "--quote", "not said")
        self.assertEqual(code, 1)
        self.assertIn("https://recorder.example/share/hc1?t=458", output)
        self.assertIn("FOUND   'eleven at night' at [00:07:55]", output)
        self.assertIn("MISSING 'not said'", output)


if __name__ == "__main__":
    unittest.main()
