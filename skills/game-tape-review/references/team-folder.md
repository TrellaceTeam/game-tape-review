# Team folder

What setup saves, where it lives and how to save it in each app. The team folder makes this the team's own copy of the skill, so a session starts with no setup questions.

## What it holds

The folder is `team/`, inside this skill's folder, beside `SKILL.md`. It holds two files:

- `team/profile.md`. The recorder, how this app gets transcripts, the link pattern, the reps, where the playbook lives, the settings, notes and the clips already played.
- `team/playbook.md`. The team's playbook, copied word for word, with where it came from. There's no copy when the team uses the built-in playbook.

The team folder never holds transcripts, run sheets or API keys. Transcripts and run sheets go in each session's work folder. For a key, the profile names only the file or setting that holds it.

## Where to look for it

1. `team/profile.md` in this skill's folder.
2. `team/profile.md` in your working folder, in a chat where setup ran earlier and the person hasn't installed the new copy yet.
3. `game-tape-review-team/profile.md` in the project folder, where setup saves when the skill's folder is read-only.
4. A profile the person attached or added to the project's files, including a `game-tape-profile.md` from an earlier version of this skill. Use it, and save it the new way at the end of the session.

## Save it

| Where the skill runs | How to save |
|---|---|
| A coding agent on the person's computer, such as Claude Code, Codex, Cursor, OpenCode, GitHub Copilot or Gemini CLI | Write the files into `team/` in this skill's folder. Read one back to check that it saved. When the folder is read-only, write them to `game-tape-review-team/` in the project folder instead, and tell the person where they are. When the team folder sits inside a git repository, as it does after an install for one project, check that git ignores it. An install for several agents can show the same folder under more than one path, such as `.agents/skills/` and `.claude/skills/`, so run `git status --short --untracked-files=all` and look for any `team/` file. If one shows, tell the person it would be committed with their playbook and reps, and ask whether to add `**/skills/game-tape-review/team/` to `.gitignore`, which covers every path |
| Claude, in a chat, the desktop app or Cowork | The skill's folder here is a copy that's gone when the chat ends. Write the changed files to a `team` folder in your working folder, then run `python <skill>/scripts/tape.py pack --team <that folder> --out <your outputs folder>/game-tape-review.skill` and share the file. `pack` keeps the team files already in the skill and lays yours over them |
| ChatGPT, Gemini or another chat app that runs Python | Run the same `pack` command with `--out <your outputs folder>/game-tape-review.zip` and share the file |
| An app that can't run code | Give `profile.md` and `playbook.md` as files or text, and ask the person to add them to a project or attach them next time |

When you share a packed file, tell the person how to install it, one step per line:

- **Claude.** "Click Save skill on this file. It installs game tape review as your own copy, with your setup inside." When no Save skill button shows: "Rename the file to game-tape-review.zip. Open Customize, then Skills. If an older game-tape-review or game-tape skill is there, delete it first. Click +, then Create skill, then Upload a skill, and pick this file."
- **ChatGPT.** "Open Plugins, then the Skills tab. If an older game-tape-review or game-tape skill is there, delete it first. Choose Create, then Upload from your computer, and pick this file."
- **Gemini.** "Unzip the file. Open Customize, then Skills. If an older game-tape-review or game-tape skill is there, delete it first. Then upload the game-tape-review folder."

`pack` names every entry `game-tape-review/...`, the shape these apps accept. Only `SKILL.md`, `references/*.md`, `scripts/*.py` and the team's `.md` files go in, so a key file, an export or a session's notes beside the skill never ship. It lists what it left out.

## Defaults

| Setting | Default | Other choices |
|---|---|---|
| Window | Last 30 days | Any number of days, or since the last session |
| Calls | First calls with outside buyers, 15 minutes or longer | Second calls, demos, renewals, or a named call |
| Calls read in full | Up to 8 per rep with subagents, up to 4 without | More, when the person asks and the session has room |
| Match | Purpose of each playbook step | Exact lines, or both |
| Clips | Sized to the minutes, as in step 5 | A number per rep |
| Swaps | Two per clip (B and C) | None, or one |
| Clip length | 1 to 3 minutes | Shorter or longer |
| Leave out | Pricing and discount talk, private details, anything that would embarrass a rep or a buyer | More topics |
| Look for | Nothing set | A step the team is working on |

## Profile template

```markdown
# Game tape review setup

Saved by the game-tape-review skill on {date}. Edit any line, or ask for a change in plain words.

## Calls
- Recorder: {name}, reached through {the connector in {app} | exported files in {folder} | an API key named {KEY_NAME} in {file}}
- Getting transcripts: {how this app gets them, such as "read them through the connector", or the person's download steps, such as "Download, Transcript, SRT, with timestamps and speaker names on"}
- Link pattern: {such as <share link>?timestamp={seconds}, checked {date} | none, scrub to the time}
- Reps:
  - {Name} <{the ID the recorder knows them by}>

## Playbook
- Playbook: {name}, from {link or file name} | the built-in first-call playbook
- Copy: team/playbook.md, copied {date}
- Match: {purpose | exact lines | both}

## Sessions
- Run by: {leader}
- Meeting: {name, when the review runs in a regular meeting | none}
- In the room: {names | not set}
- Review length: {minutes} minutes | ask each time
- Who's on tape: {every rep | my own calls, to teach | one rep, for a 1:1}

## Settings
- Window: {last 30 days}
- Calls: {first calls with outside buyers, 15 minutes or longer}
- Clips: {sized to the minutes}
- Swaps: {two per clip}
- Clip length: {1 to 3 minutes}
- Leave out: {pricing and discount talk, private details}
- Look for: {nothing set}

## Notes
- {date}: {what the leader liked or changed, in their words, such as "match the job of a step, not the literal line"}

## Played
- {session date}: {rep}, {good or pause}, {account} {call date}, {start} to {end}
```

## Playbook copy

Start `team/playbook.md` with one line on where it came from, such as "Copied from Sales playbook (Google Drive, <link>) on 2026-10-16." Then copy the playbook's words as they are, with its headings and lists. Leave out images. Copy all of it, however long, and never summarize it.

## Keeping it current

- Write settings as standing rules, such as "last 30 days", never one session's dates.
- Under Played, list each session's recommended clips, so the next session picks new moments. Keep the last eight sessions and drop older lines.
- Add a dated note only when the person says it should hold next time, or makes the same change twice.
- Change the profile at setup and at the end of a session, never in the middle.
