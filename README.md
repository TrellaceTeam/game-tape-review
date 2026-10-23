# Game tape review

A game tape review is when a sales team watches short clips of its own calls and talks about them, the way a sports team studies film of its own plays. This is a skill, a set of steps your AI assistant follows, and it preps a game tape review for you. It reads your recorded calls and your sales playbook. For each rep, it picks one clip of a playbook step done well and one clip to pause on, where the room says what they'd do next. Every clip comes with its start time, a link where your recorder allows one, a one-line setup, the exact quotes and questions for the room.

It's built for Claude, ChatGPT, Gemini and coding tools such as Claude Code, Codex and Cursor. It reads calls from Fathom, Fireflies, Gong, Grain, Avoma, Otter, Read AI, tl;dv, Zoom, Google Meet, Microsoft Teams or any transcript file. So far we've tested it end to end only in Claude Code. <!-- prose-allow: semicolon -->

## Install it

Paste this into your AI assistant, such as Claude, ChatGPT, Gemini or a coding agent:

```text
Set up this skill and install it for me: https://github.com/TrellaceTeam/game-tape-review
```

Your assistant follows [INSTALL.md](INSTALL.md). It sets the skill up with you first, then installs your own copy with your setup inside, so you install it once.

If you can, connect your call recorder to your assistant before you paste the line. In Claude, that's Customize, then Connectors. In ChatGPT, it's Plugins. Some apps see a new connection only in a new chat. When yours does, your assistant tells you what to click and gives you a line to paste there.

To install it yourself, INSTALL.md has the steps for each app.

## Setup takes about five minutes

The assistant asks one question at a time.

1. **Your recorder.** It looks for a call recorder you've connected and asks, "Is that where your sales calls are?" When none is connected, it shows you how to connect yours.
2. **Your reps.** It lists who ran calls with outside buyers in the last 30 days, and you pick who's on tape.
3. **Your playbook.** Point it at the doc in Google Drive, Notion or another connected app, or drop the file in. It keeps a copy and re-reads the original each time. No playbook? It uses a [built-in first-call playbook](skills/game-tape-review/references/first-call-playbook.md).
4. **Your clip links.** It works out how your recorder links to a moment in a call, and asks you to click one test link.
5. **Your time.** It asks how many minutes a game tape review usually gets.

It saves all of this inside your own copy of the skill. In a coding tool, it saves it for you. In Claude, ChatGPT or Gemini, it hands you your copy as one file to save.

## Then ask for a game tape review

Type "Prep a game tape review" whenever you want one. It skips the setup questions and uses what it saved. Add anything this review needs:

- "Game tape review for Thursday's sales meeting, 20 minutes."
- "Only Jordan's calls, for our 1:1."
- "My own calls, to teach our first AE." It picks four to six good clips in call order.
- "Look for how we get the person who signs the deal onto the next call."
- "Use the last two weeks, and skip anything with pricing in it."

It reads your recent calls and hands back a run sheet. Changes you want to keep go into your setup, and so does a list of clips you've played, so the next review picks new moments. In a chat app, it hands you an updated file to save for that.

## What you get

The run sheet is a document you can paste into a meeting agenda. It opens with a script for the leader and a table of picks, with two backup clips for each pick. Then comes one block per clip. Here's part of a pause clip from [the example](examples/fennick/README.md), a full setup and review on five calls from Fennick Software, a fictional company.

> ### 2. Priya, pause: Sable Point (Oct 13, first call)
>
> **Why this step matters.** When a buyer says "I'll run it by my boss," that's the moment to learn who the boss is and ask to put them on the next call. If it passes, the buyer carries our case alone and the next step becomes an email.
>
> **Set it up.** Greg runs maintenance at Sable Point Packaging, a one-plant corrugated box maker. Priya has just finished a long demo and answered Greg's price question. The clip starts after the price talk. <!-- prose-allow: just -->
>
> **Play part 1: [15:22 to 15:54](https://recorder.example/share/q5Ws1Sable1013?t=922).** Pause right after Greg says "[00:15:43] I like it. I really do. I'll need to run it by my boss. He'll want to see numbers." <!-- prose-allow: really -->
>
> **Ask the room while it's paused.**
> 1. What would you say next?
>
> **What came before.** The answer key, to share after the room answers.
> - 12:02. "[00:12:02] Does that break it out by machine? My plant manager, Neil Ostrowski, keeps asking me why the corrugator keeps going down."
> - 9:31. "[00:09:31] Sorry, one thing before you move on. I've got budget left this year if we move before December."
>
> **Play part 2: [15:54 to 16:40](https://recorder.example/share/q5Ws1Sable1013?t=954).**
>
> **The near-miss.** Greg named the boss, Neil, and said Neil keeps asking about the corrugator. Greg also said there's budget this year if they move before December. The call ends with Greg saying "[00:16:33] Perfect. Yeah, I'll get back to you next week or so." We don't know who signs, and no meeting is booked. Priya could say:
> - "Neil keeps asking why the corrugator goes down. Would he join a 30 minute look at that downtime report with you? Who else weighs in before you'd move ahead?"

A script that ships with the skill checks every quote against its transcript line, and every link against its start time. When a quote is off, the script prints the right time or the real words, and the assistant fixes it.

## Run the review

Each review runs in five steps, and the run sheet's script follows them.

1. **The person on the call speaks first.** Before anyone else weighs in, they say what they were going for.
2. **Play the good clip.** Ask what made it work, and where else it would help.
3. **Play the pause clip and stop at the pause.** Ask "What would you say next?" Then play on, and share what the buyer said earlier.
4. **Each person adds one thing that worked and one thing to try.** Keep it about the move, never the person.
5. **Pick one thing the whole team tries next.** Tell the skill, and the next review looks for it.

## Recorders

| Recorder | How the skill gets your calls | Links open at the right moment |
|---|---|---|
| Fathom | Connect it in your assistant | Yes |
| Gong | Download transcripts, or Gong's API in a coding agent | Yes, for viewers signed in to Gong |
| Fireflies, Grain, Otter, Read AI, tl;dv <!-- prose-allow: semicolon --> | Connect it in your assistant. Fireflies, Grain and Otter also download transcripts | Fireflies and tl;dv from one copied link. Grain and Otter through their own clips. Read AI, no |
| Avoma | Connect it, or download transcripts | No. Use its public snippets |
| Zoom, Microsoft Teams | Download transcripts | No. The run sheet says where to scrub to |
| Google Meet | Through Google Drive | From Drive's copied link, within about 5 minutes |
| Anything else | Upload transcripts as VTT, SRT, DOCX, JSON or TXT | From one copied link, when the recorder makes one |

In Claude, ChatGPT and Gemini chats, the skill uses your recorder to pick the calls, then asks you to download those few transcripts. That way the script can check every quote. In a coding agent, it reads them straight from the recorder. [recorders.md](skills/game-tape-review/references/recorders.md) has the details for each recorder.

## What it touches

- **Read only.** It lists and reads calls and docs. It never creates, edits, shares or deletes anything in your recorder or your docs. Some recorder connections can also share or delete, so to be sure, switch those tools off in the connection's settings.
- **Your setup.** Your copy of the skill holds a `team` folder with your recorder, reps, link pattern, playbook copy and the clips you've played. It holds no transcripts and no keys. Share your copy only with people who should see your playbook.
- **Each review's files.** Transcripts and the run sheet go in a work folder, `game-tape-review-<date>/`. It holds buyers' names, so keep it out of anything you share.
- **Keys.** It never asks for an API key in chat.
- **The room.** Buyers agreed to be recorded for the call, not to be shown widely. The skill skips sensitive moments, and the clips are for your team only.

## Limits

- Fathom and Gong links open at a set second. Fireflies, tl;dv and Google Meet need one copied link first. Other recorders need a clip made in the recorder, or a time to scrub to. <!-- prose-allow: semicolon -->
- Google Meet's transcript marks the time only every 5 minutes, so Meet clips land within about 5 minutes. The leader finds the moment by its words.
- A chat holds about 10 to 15 full calls. Coding agents that can split the reading across helpers read more.
- Transcripts sometimes mislabel speakers, and their times can sit a few seconds off the video. Each clip starts a few seconds early.
- It picks moments. You decide what plays, so watch every clip before the review.
- We've run install, setup and a review end to end in Claude Code. We haven't yet tested the Claude, ChatGPT and Gemini routes, and the Save skill button in Claude comes from Anthropic's docs. We checked every recorder's docs in October 2026, and vendors change their menus often.

## What's in this repo

| Path | What it's for |
|---|---|
| [skills/game-tape-review/](skills/game-tape-review/SKILL.md) | The skill: its steps, setup, writing rules, recorder notes and the `tape.py` script |
| [INSTALL.md](INSTALL.md) | How an assistant, or you, sets it up and installs it in each app |
| [prompts/game-tape-review.md](prompts/game-tape-review.md) | A paste-in version for assistants without skills |
| [examples/fennick/](examples/fennick/README.md) | A full fictional setup and review: the calls, the playbook, the saved setup and the run sheet |

## From Trellace

[Trellace](https://www.trellace.com/?utm_source=github&utm_medium=readme&utm_campaign=game-tape-review) helps B2B startups become scaleups. That 'messy middle' phase, after product-market fit and before a repeatable go-to-market team. We built this skill so any founder can run a game tape review session with the tools they already have. We believe GTM needs more open source projects. 

- **Founders.** If something here is close to what you're working through, [book a 30-minute GTM Sparring Session](https://www.trellace.com/contact?utm_source=github&utm_medium=readme&utm_campaign=game-tape-review).
- **Investors.** If a company you back comes to mind, [make an introduction](https://www.trellace.com/contact?utm_source=github&utm_medium=readme&utm_campaign=game-tape-review).
- **More free tools.** See everything we've published at [github.com/TrellaceTeam](https://github.com/TrellaceTeam).

## License

[MIT](LICENSE). Use it, change it and ship it, including for commercial work.
