# Install game tape

These steps are for the AI assistant a person asked to "install this for me". A person can follow them by hand too. Installing takes a minute. Setup follows straight after, in the same conversation, and takes about five.

1. **Work out where you're running.** Done when you know which section below is yours.
2. **Install the skill.** Done when the skill's `SKILL.md` is where your app will load it next time, or the person has a file to save.
3. **Run setup now.** Done when the person's setup is saved inside their copy of the skill.

## 1. Work out where you're running

| You are | Follow |
|---|---|
| A coding agent with a terminal, such as Claude Code, Codex, Cursor, OpenCode, GitHub Copilot or Gemini CLI | [Coding agents](#coding-agents) |
| Claude, in a chat, the desktop app or Cowork | [Claude](#claude) |
| ChatGPT | [ChatGPT](#chatgpt) |
| Gemini | [Gemini](#gemini) |
| Any other assistant | [Anything else](#anything-else) |

## 2. Install the skill

### Coding agents

1. Run `node --version`. With Node.js 22.20 or later, install for every project on this computer:

   ```
   npx skills add https://github.com/TrellaceTeam/sales-game-tape -g -y
   ```

   Leave out `-g` when the person wants it in this folder only. When they gave you a link to a branch or a fork, use their link.
2. Without Node.js 22.20, download [game-tape.zip](https://github.com/TrellaceTeam/sales-game-tape/releases/latest/download/game-tape.zip), unzip it, and copy the `game-tape` folder into your skills folder: `~/.claude/skills/` for Claude Code, and `~/.agents/skills/` for Codex, Cursor, OpenCode, GitHub Copilot and Gemini CLI.
3. Find the installed `SKILL.md` and note its folder. That's `<skill>` in the skill's steps.

### Claude

You can't add a skill to the person's account yourself. You can hand them a file with a Save skill button, so they install it with one click. Run setup first, so that file already holds their setup.

1. Code execution must be on. If you can't run code, ask the person to turn on "Code execution and file creation" under Settings, then Capabilities. On a Team or Enterprise plan, an owner may need to allow it and allow skills.
2. Download the skill into your working folder and unzip it:

   ```
   curl -fsSL -o game-tape.zip https://github.com/TrellaceTeam/sales-game-tape/releases/latest/download/game-tape.zip
   ```

   When the download is blocked, ask the person to download [game-tape.zip](https://github.com/TrellaceTeam/sales-game-tape/releases/latest/download/game-tape.zip) and drop it into this chat.
3. Run setup from the unzipped `game-tape` folder. It ends by packing the skill with the person's setup inside as `game-tape.skill`, for them to save.

When the person wants to stop before setup ends, run `python game-tape/scripts/tape.py pack --out <your outputs folder>/game-tape.skill` and share that file to save. Setup runs the first time they ask for game tape.

### ChatGPT

Skill uploads work on ChatGPT Business, Enterprise, Healthcare and Edu. We haven't tested this route yet.

1. Ask the person whether they see a Skills tab under Plugins. Without it, follow [Anything else](#anything-else).
2. Ask them to download [game-tape.zip](https://github.com/TrellaceTeam/sales-game-tape/releases/latest/download/game-tape.zip) and attach it here. Unzip it in your Python tool.
3. Run setup from the unzipped `game-tape` folder. It ends by packing the skill with their setup inside as `game-tape.zip`. They upload it under Plugins, then Skills, then Create, then Upload from your computer.

### Gemini

Gemini needs the person to upload the folder. We haven't tested this route yet.

1. Ask them to download [game-tape.zip](https://github.com/TrellaceTeam/sales-game-tape/releases/latest/download/game-tape.zip) and unzip it.
2. Then Customize, then Skills, then Upload, and pick the `game-tape` folder.
3. Ask them to start a new chat and say "set up game tape".

### Anything else

Use [the paste-in prompt](prompts/game-tape.md). It runs the core of the skill on transcripts the person attaches. It can't save a setup, so each time they paste it, they fill in four lines.

## 3. Run setup now

Read `SKILL.md` in the installed or unzipped folder, then follow its `references/setup.md` in this conversation. Don't wait for a new session. Start with one line, such as "Installed. Setup takes about five minutes, one question at a time." Then ask the first question.

## Update it later

The person can ask: "Update game tape from https://github.com/TrellaceTeam/sales-game-tape and keep my setup."

- **Coding agents.** Copy the skill's `team/` folder somewhere safe, install again as above, then copy `team/` back into the new skill folder. Check that `team/profile.md` is there.
- **Chat apps.** Read the team files from the installed skill's `team/` folder, get the new zip as above, and run `python game-tape/scripts/tape.py pack --team <the old team folder> --out <your outputs folder>/game-tape.skill`. Use `game-tape.zip` as the name outside Claude. Share the file to save in place of the old one.
