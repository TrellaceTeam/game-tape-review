# Install game tape review

These steps are for the AI assistant a person asked to set up and install this skill, or only to install it. Most people who paste the link aren't technical. They copied one line from the README and expect you to do the rest, one question at a time. A person can follow these steps by hand too.

Setup comes before the install. The copy the person installs then already holds their setup, so they install it once. Setup takes about five minutes.

1. **Work out where you're running.** Done when you know which section below is yours.
2. **Get the skill.** Done when you can read its `SKILL.md`. In a coding agent, that's the installed copy.
3. **Set it up.** Done when the person's setup is saved, or the person has a line to paste in a new chat.
4. **Install their copy.** Done when the copy with their setup is where their app loads it, or in a chat app the person has the file and the steps to install it.

Whenever the person has to open a new chat, such as after connecting their call recorder, give them the line to paste there, as [setup.md](skills/game-tape-review/references/setup.md#moving-to-a-new-chat) says. Then stop. The new chat goes on from that line.

## 1. Work out where you're running

| You are | Follow |
|---|---|
| A coding agent with a terminal, such as Claude Code, Codex, Cursor, OpenCode, GitHub Copilot or Gemini CLI | [Coding agents](#coding-agents) |
| Claude, in a chat, the desktop app or Cowork | [Claude](#claude) |
| ChatGPT | [ChatGPT](#chatgpt) |
| Gemini | [Gemini](#gemini) |
| Any other assistant | [Anything else](#anything-else) |

## 2. Get the skill

### Coding agents

1. Run `node --version`. With Node.js 22.20 or later, install for every project on this computer:

   ```
   npx skills add https://github.com/TrellaceTeam/game-tape-review -g -y
   ```

   Leave out `-g` when the person wants it in this folder only. When they gave you a link to a branch or a fork, use their link.
2. Without Node.js 22.20, download [game-tape-review.zip](https://github.com/TrellaceTeam/game-tape-review/releases/latest/download/game-tape-review.zip), unzip it, and copy the `game-tape-review` folder into your skills folder: `~/.claude/skills/` for Claude Code, and `~/.agents/skills/` for Codex, Cursor, OpenCode, GitHub Copilot and Gemini CLI.
3. Find the installed `SKILL.md` and note its folder. That's `<skill>` in the skill's steps.

Setup saves into this installed copy, so step 4 has nothing left to do.

### Claude

You can't add a skill to the person's account yourself. Claude shows a Save skill button on skill files it shares, so you set up a copy here and hand it over at the end, with the setup inside. We haven't tested this route end to end yet.

1. **Check that you can run code.** When you can't, ask the person to turn on "Code execution and file creation" under Settings, then Capabilities. On a Team or Enterprise plan, an owner may need to allow it and allow skills. When their call recorder isn't connected yet, ask them to connect it too, under Customize, then Connectors. Then move to a new chat, as [setup.md](skills/game-tape-review/references/setup.md#moving-to-a-new-chat) says. When code has to stay off, follow [Anything else](#anything-else).
2. **Download the skill** into your working folder and unzip it:

   ```
   curl -fsSL -o game-tape-review.zip https://github.com/TrellaceTeam/game-tape-review/releases/latest/download/game-tape-review.zip
   ```

   When the download is blocked, ask the person to download [game-tape-review.zip](https://github.com/TrellaceTeam/game-tape-review/releases/latest/download/game-tape-review.zip) and drop it into this chat.

### ChatGPT

Skill uploads work on ChatGPT Business, Enterprise, Healthcare and Edu. We haven't tested this route yet.

1. Ask the person whether they see Plugins in the sidebar, with a Skills tab. Without it, follow [Anything else](#anything-else).
2. Ask them to download [game-tape-review.zip](https://github.com/TrellaceTeam/game-tape-review/releases/latest/download/game-tape-review.zip) and attach it here. Unzip it in your Python tool.

### Gemini

We haven't tested this route yet.

1. Ask the person to download [game-tape-review.zip](https://github.com/TrellaceTeam/game-tape-review/releases/latest/download/game-tape-review.zip) and attach it here. Unzip it with your code tool.
2. When you can't unzip it or run Python, ask them to unzip it themselves, open Customize, then Skills, then Upload, and pick the `game-tape-review` folder. Then move to a new chat, as [setup.md](skills/game-tape-review/references/setup.md#moving-to-a-new-chat) says. Setup runs there, and it tells them how to save their setup.

### Anything else

Use [the paste-in prompt](prompts/game-tape-review.md). It runs the core of the skill on transcripts the person attaches. It can't save a setup, so each time they paste it, they fill in four lines.

## 3. Set it up

Skip this step and step 4 for the paste-in prompt, which has no setup and nothing to install.

Read `SKILL.md` in the installed or unzipped folder, then follow its `references/setup.md` now, in this conversation. Start with one line, such as "Got it. Setup takes about five minutes, one question at a time." Then ask the first question.

## 4. Install their copy

Setup's last step saves the team folder the way [team-folder.md](skills/game-tape-review/references/team-folder.md#save-it) says for this app.

- **Coding agents.** It saves into the installed copy, and you're done.
- **Chat apps.** It packs the skill with the person's setup inside and hands them the file, with the steps to install it.

When the person wants to stop before setup ends, give them a line to paste when they come back, with what they've answered so far, as [setup.md](skills/game-tape-review/references/setup.md#moving-to-a-new-chat) says. They install once, when setup is done.

## Update it later

The person can ask: "Update game tape review from https://github.com/TrellaceTeam/game-tape-review and keep my setup."

- **Coding agents.** Copy the skill's `team/` folder somewhere safe, install again as above, then copy `team/` back into the new skill folder. Check that `team/profile.md` is there. Versions before 1.2 named the skill `game-tape`. When that older skill is installed, copy its `team/` folder into the new one, then remove the old skill so the two don't both answer.
- **Chat apps.** Copy the installed skill's `team/` folder to your working folder, get and unzip the new zip as above, and run `python game-tape-review/scripts/tape.py pack --team <the copied team folder> --out <your outputs folder>/game-tape-review.skill`. Use `game-tape-review.zip` as the name outside Claude. Share the file to save in place of the old one.
