# Game tape for your sales team

Game tape is when a sales team watches short clips of its own calls and talks about them, the way a sports team watches its own plays. This skill preps it for you. It reads your recorded calls and your sales playbook. For each rep, it picks one clip of a playbook step done well and one clip to pause on, where the room says what they'd do next. Every clip comes with a link that opens at the right moment, a one-line setup, the exact quotes and questions for the room.

It works in Claude, ChatGPT, Gemini and coding agents. It reads calls from Fathom, Fireflies, Gong, Grain, Avoma, Otter, Read AI, tl;dv, Zoom, Google Meet, Microsoft Teams or any transcript file. <!-- prose-allow: semicolon -->

## Install it

Copy this page's link into your AI assistant and say:

```text
Install this for me: https://github.com/TrellaceTeam/sales-game-tape
```

Your assistant follows [INSTALL.md](INSTALL.md). It installs the skill, then walks you through setup. To install it yourself, the same file has the steps for each app.

## Setup takes about five minutes

The assistant asks one question at a time.

1. **Your recorder.** It looks for a call recorder you've connected and asks, "Is that where your sales calls are?" When none is connected, it shows you how to connect yours.
2. **Your reps.** It lists who ran calls with outside buyers in the last 30 days, and you pick who's on tape.
3. **Your playbook.** Point it at the doc in Google Drive, Notion or another connected app, or drop the file in. It keeps a copy and re-reads the original each time. No playbook? It uses a [built-in first-call playbook](skills/game-tape/references/first-call-playbook.md).
4. **Your clip links.** It works out how your recorder links to a moment in a call, and asks you to click one test link.
5. **Your time.** How many minutes game tape usually gets.

It saves all of this inside your own copy of the skill. In a coding agent, it saves it for you. In Claude, ChatGPT or Gemini, it hands you your copy as one file to save.

## Then ask for game tape

Type "Prep game tape" whenever you want a session. It skips the setup questions and uses what it saved. Add anything this session needs:

- "Game tape for Thursday's sales meeting, 20 minutes."
- "Only Jordan's calls, for our 1:1."
- "My own calls, to teach our first AE." It picks four to six good clips in call order.
- "Look for how we get the person who signs onto the next call."
- "Use the last two weeks, and skip anything with pricing in it."

It reads your recent calls and hands back a run sheet. Changes you want to keep go into your setup, and so does a list of clips you've played, so the next session picks new moments.

## What you get

The run sheet is a Markdown file, ready to paste into a meeting agenda. It opens with a script for the leader and a table of picks, with two swaps for each clip. Then comes one block per clip. Here's a pause clip from [the example](examples/fennick/README.md), a full run on five calls from Fennick Software, a fictional company.

> ### 4. Priya, pause: Sable Point Packaging (Oct 13, first call)
>
> **Why this step matters.** Same step, one week later. A buyer who says "I need to run it by my boss" is handing you the decision maker. The next question decides whether the boss ever meets you.
>
> **Set it up.** Greg is the maintenance manager at Sable Point, a 250-person corrugated box plant. He took the call because of three corrugator stops in August. Priya has just finished a full demo, and Greg has said the price is reasonable. <!-- prose-allow: just -->
>
> **Play part 1: [15:30 to 15:43](https://recorder.example/share/q5Ws1Sable1013?t=930).** Pause right after Greg says "[00:15:43] I like it. I really do. I'll need to run it by my boss. He'll want to see numbers." <!-- prose-allow: really -->
>
> **Ask the room while it's paused.**
> 1. What would you say next?
> 2. What do you want to know about the boss before you hang up?
>
> **What came before.** The answer key:
> - 9:31. "[00:09:31] Sorry, one thing before you move on. I've got budget left this year if we move before December."
> - 12:02. "[00:12:02] Does that break it out by machine? My plant manager, Neil Ostrowski, keeps asking me why the corrugator keeps going down."
>
> **Play part 2: [15:43 to 16:33](https://recorder.example/share/q5Ws1Sable1013?t=943).**
>
> **The near-miss.** The call ended on "send some things and let me know". Nothing was booked and Neil was never asked about. Priya could have said:
> - "What will Neil want to see? Could he join us for 30 minutes next week? I have two times."

A script that ships with the skill checks every quote against its transcript line, and every link against its start time. When a quote is off, the script prints the right time or the real words, and the assistant fixes it.

## Run the session

The run sheet opens with a script for the leader. The format behind it:

1. **The person on the call speaks first.** Before anyone else weighs in, they say what they were going for.
2. **Play the good clip.** Ask what made it work, and where else it would help.
3. **Play the pause clip and stop at the pause.** Ask "What would you say next?" Then play on, and share what the buyer said earlier.
4. **Each person adds one thing that worked and one thing to try.** Keep it about the move, never the person.
5. **Pick one thing the whole team tries next.** Tell the skill, and the next session looks for it.

## Recorders

| Recorder | How the skill gets your calls | Links open at the right moment |
|---|---|---|
| Fathom | Connect it in your assistant | Yes |
| Gong | Download transcripts, or Gong's API in a coding agent | Yes, for viewers signed in to Gong |
| Fireflies, Grain, Otter, Read AI, tl;dv <!-- prose-allow: semicolon --> | Connect it in your assistant, or download transcripts | Fireflies and tl;dv from one copied link. Grain and Otter through their own clips |
| Avoma | Connect it, or download transcripts | No. Use its public snippets |
| Zoom, Microsoft Teams | Download transcripts | No. The run sheet says where to scrub to |
| Google Meet | Through Google Drive | From Drive's copied link, within about 5 minutes |
| Anything else | Upload transcripts as VTT, SRT, DOCX, JSON or TXT | From one copied link, when the recorder makes one |

In Claude, ChatGPT and Gemini chats, the skill uses your recorder to pick the calls, then asks you to download those few transcripts. That way the script can check every quote. In a coding agent, it reads them straight from the recorder. [recorders.md](skills/game-tape/references/recorders.md) has the details for each recorder.

## What it touches

- **Read only.** It lists and reads calls and docs. It never creates, edits, shares or deletes anything in your recorder or your docs. Some recorder connections can also share or delete, so to be sure, switch those tools off in the connection's settings.
- **Your setup.** Your copy of the skill holds a `team` folder with your recorder, reps, link pattern, playbook copy and the clips you've played. It holds no transcripts and no keys. Share your copy only with people who should see your playbook.
- **Each session's files.** Transcripts and the run sheet go in a work folder, `game-tape-<date>/`. It holds buyers' names, so keep it out of anything you share.
- **Keys.** It never asks for an API key in chat.
- **The room.** Buyers agreed to be recorded for the call, not to be shown widely. The skill skips sensitive moments, and the clips are for your team only.

## Limits

- Only Fathom and Gong document links that open at a set second. Other recorders need one copied link, a clip made in the recorder, or a time to scrub to.
- Google Meet's transcript marks the time only every 5 minutes, so Meet clips land within about 5 minutes. The leader finds the moment by its words.
- A chat holds about 10 to 15 full calls. Coding agents that can split the reading across helpers read more.
- Transcripts sometimes mislabel speakers, and their times can sit a few seconds off the video. Each clip starts a few seconds early.
- It picks moments. You decide what plays, so watch every clip before the session.
- We've run install, setup and sessions end to end in Claude Code. We haven't yet tested the Claude, ChatGPT and Gemini routes, and the one-click Save skill in Claude comes from Anthropic's docs. We checked every recorder's docs in October 2026, and vendors change their menus often.

## What's in this repo

| Path | What it's for |
|---|---|
| [skills/game-tape/](skills/game-tape/SKILL.md) | The skill: its steps, setup, writing rules, recorder notes and the `tape.py` script |
| [INSTALL.md](INSTALL.md) | How an assistant, or you, installs it in each app |
| [prompts/game-tape.md](prompts/game-tape.md) | A paste-in version for assistants without skills |
| [examples/fennick/](examples/fennick/README.md) | A full fictional setup and session: the calls, the playbook, the saved setup and the run sheet |

## From Trellace

[Trellace](https://www.trellace.com/?utm_source=github&utm_medium=readme&utm_campaign=sales-game-tape) works with B2B founders in the messy middle, after product-market fit and before a repeatable go-to-market team. That's usually $1 million to $10 million in annual revenue. We built this skill to prep game tape for a sales team we work with, then rebuilt it so any founder can run it with the tools they already have. We publish the methods we use because GTM needs more open source projects.

- **Founders.** If something here is close to what you're working through, [book a 30-minute GTM Sparring Session](https://www.trellace.com/contact?utm_source=github&utm_medium=readme&utm_campaign=sales-game-tape).
- **Investors.** Most of our work starts with an introduction from a fund. If a company you back comes to mind, [make an introduction](https://www.trellace.com/contact?utm_source=github&utm_medium=readme&utm_campaign=sales-game-tape).
- **More free tools.** See everything we've published at [github.com/TrellaceTeam](https://github.com/TrellaceTeam).

## License

[MIT](LICENSE). Use it, change it and ship it, including for commercial work.
