# A full run on five fictional calls

This folder holds one complete game-tape run: the five calls that went in, and the run sheet and team profile that came out. Fennick Software, its prospects and everyone in them are fictional.

Fennick sells maintenance planning software to manufacturers. Priya Raman, the CEO, still runs many first calls, and Jordan Ellis is the first account executive. The run prepared game tape for their Monday sales meeting, with 30 minutes for tape and one thing to look for: getting the person who signs onto the next call.

## What went in

Each call is in a different export format, the way different recorders give them, so the run also shows the converter at work.

| Call | Rep | Date | Format |
|---|---|---|---|
| [Ashgrove Plastics, discovery](calls/ashgrove-discovery-2026-09-22.txt) | Jordan | Sep 22 | Text, `[00:00:13] Name: text` |
| [Pell Valley Components, intro](calls/pell-valley-intro-2026-09-24.txt) | Jordan | Sep 24 | Text, a `Name  00:08` line with the words below |
| [Ashgrove Plastics, working session](calls/ashgrove-working-session-2026-09-30.vtt) | Jordan | Sep 30 | WebVTT |
| [Harrow Creek Castings, first call](calls/harrow-creek-first-call-2026-10-06.srt) | Priya | Oct 6 | SubRip, a few seconds per cue |
| [Sable Point Packaging, first call](calls/sable-point-first-call-2026-10-13.json) | Priya | Oct 13 | JSON from an API, one sentence per item |

[links.txt](calls/links.txt) holds each call's share link. The links point to `recorder.example`, a made-up address, so they don't open.

## What came out

| File | What it is |
|---|---|
| [game-tape-2026-10-19/run-sheet.md](game-tape-2026-10-19/run-sheet.md) | The run sheet the meeting runs from |
| [game-tape-2026-10-19/transcripts/](game-tape-2026-10-19/transcripts/priya/2026-10-13-sable-point.txt) | The five calls, converted to the tape format |
| [game-tape-profile.md](game-tape-profile.md) | The team profile, so next week starts with one question |

## How it was made

We ran the skill once in Claude Code with Claude Sonnet 5.5, on October 16, 2026, and copied what it wrote into this folder. Nothing was edited by hand. The run took under 3 minutes. It read all five calls itself, without subagents, and its own check found 0 problems in 55 quotes and 16 links. This was the prompt:

```text
I'm Priya Raman, CEO of Fennick Software. Prep game tape for our sales meeting on Monday. I'm not around to answer questions, so here is everything:

- Calls: transcript exports from our recorder are in the calls folder. Each call's share link is in calls/links.txt.
- Playbook: we don't have one written down. Use the built-in one.
- Who's on tape: every rep. That's me (priya@fennick.example) and Jordan Ellis (jordan@fennick.example).
- Meeting: Fennick weekly sales meeting, Monday October 19, 2026, 9:00 Eastern. I run it. Jordan, Mei Tanaka and I are in the room. Game tape gets 30 minutes.
- Look for: getting the person who signs onto the next call.

Work in this folder.
```

The prompt answers the skill's four questions up front because nobody was there to answer them. In normal use, the skill asks.

A few things the run did on its own: it warned Priya that her own call is on tape and to watch it first, it built Jordan's pause clip across two calls so the room sees a promise made on one call and missed on the next, and it kept every clip short of the pricing talk.

## Check it yourself

From the repo root:

```
python skills/game-tape/scripts/tape.py check examples/fennick/game-tape-2026-10-19/run-sheet.md examples/fennick/game-tape-2026-10-19/transcripts
```

The repo's tests run the same check on every push, and convert each call again to make sure no word changes.
