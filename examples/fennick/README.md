# A full setup and game tape review on five fictional calls

This folder holds one complete run: the calls and playbook that went in, the setup the skill saved, and the run sheet from its first game tape review. Fennick Software, its prospects and everyone in them are fictional.

Fennick sells maintenance planning software to manufacturers. Priya Raman, the CEO, still runs many first calls, and Jordan Ellis is the first account executive. Their playbook says a first call has one goal: a second meeting on the calendar with the person who signs.

## What went in

Each call is in a different export format, the way different recorders give them, so the run also shows the converter at work.

| Call | Rep | Date | Format |
|---|---|---|---|
| [Ashgrove Plastics, discovery](calls/ashgrove-discovery-2026-09-22.txt) | Jordan | Sep 22 | Text, `[00:00:13] Name: text` |
| [Pell Valley Components, intro](calls/pell-valley-intro-2026-09-24.txt) | Jordan | Sep 24 | Text, a `Name  00:08` line with the words below |
| [Ashgrove Plastics, working session](calls/ashgrove-working-session-2026-09-30.vtt) | Jordan | Sep 30 | WebVTT |
| [Harrow Creek Castings, first call](calls/harrow-creek-first-call-2026-10-06.srt) | Priya | Oct 6 | SubRip, a few seconds per cue |
| [Sable Point Packaging, first call](calls/sable-point-first-call-2026-10-13.json) | Priya | Oct 13 | JSON from an API, one sentence per item |

[links.txt](calls/links.txt) holds each call's share link. The links point to `recorder.example`, a made-up address, so they don't open. [fennick-first-call-playbook.md](fennick-first-call-playbook.md) is the team's six-step playbook.

## What came out

| File | What it is |
|---|---|
| [team/profile.md](team/profile.md) | The setup the skill saved inside its own folder, with the review's four clips under Played |
| [team/playbook.md](team/playbook.md) | Setup's word-for-word copy of the playbook |
| [game-tape-review-2026-10-16/run-sheet.md](game-tape-review-2026-10-16/run-sheet.md) | The run sheet the meeting runs from |
| [game-tape-review-2026-10-16/transcripts/](game-tape-review-2026-10-16/transcripts/priya/2026-10-13-sable-point.txt) | The five calls, converted to the tape format |

## How it was made

We ran Claude Code with Claude Sonnet 5.5 twice on October 16, 2026, in a folder that held only the calls and the playbook. We copied what it wrote into this folder, and nothing was edited by hand.

**1. Install and setup, in 40 seconds.** It read [INSTALL.md](../../INSTALL.md), installed the skill from GitHub into the folder, copied the playbook and saved the setup. This was the prompt:

```text
Install this for me: https://github.com/TrellaceTeam/game-tape-review

Install it for this folder only, not for every project.

I'm Priya Raman, CEO of Fennick Software. I can't answer questions live today, so here are my answers to the setup questions. Don't wait for me:

- Recorder: none is connected in this app. Our transcript exports are in the calls folder, and each call's share link is in calls/links.txt.
- Reps: me (priya@fennick.example) and Jordan Ellis (jordan@fennick.example).
- Playbook: it's the file fennick-first-call-playbook.md in this folder. File it away so you always have it.
- Links: when you give me a test link, assume I clicked it and it opened at the right moment.
- Time: a game tape review gets 30 minutes in our Monday sales meeting, which I run.

Don't prep a review yet. Work in this folder.
```

The prompt answers setup's questions up front because nobody was there to answer them. In normal use, the assistant asks them one at a time.

**2. A game tape review, in 3 minutes and 28 seconds.** A new conversation, with this prompt:

```text
Prep a game tape review for our sales meeting on Monday, October 19, 2026. Look for how we get the person who signs onto the next call. Work in this folder.
```

It asked no questions. It read the saved setup, converted the five calls, and its check found 0 problems in 41 quotes and 13 links.

A few things it did on its own:

- It built all four clips around step 5 of the playbook, so the room follows one thread.
- It built Jordan's pause clip across two calls. On Sep 22 Jordan promised to ask about the CFO's calendar at the end of the next meeting, and the Sep 30 call ends without that ask.
- It left out the Pell Valley call, because it ran 12 minutes, under the 15-minute cutoff.
- It ended each clip before the pricing talk, and listed where the pricing sits so the leader can stop in time.

## Check it yourself

From the repo root:

```
python skills/game-tape-review/scripts/tape.py check examples/fennick/game-tape-review-2026-10-16/run-sheet.md examples/fennick/game-tape-review-2026-10-16/transcripts
```

The repo's tests run the same check on every push. They also convert each call again to make sure no word changes, and check that the playbook copy matches the original word for word.
