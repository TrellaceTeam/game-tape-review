# Team profile

The template for `game-tape-profile.md` and the defaults for every setting. The profile holds a team's answers and settings, so the next run asks one question instead of four. The person can edit it by hand or ask for a change in plain words, such as "use the last two weeks" or "two clips each for Jordan".

## Defaults

| Setting | Default | Other choices |
|---|---|---|
| Window | Last 30 days | Any number of days, or since the last game tape |
| Calls | First calls with outside buyers, 15 minutes or longer | Second calls, demos, renewals, or a named call |
| Calls read in full | Up to 8 per rep with subagents, up to 4 without | More, when the person asks and the session has room |
| Match | Purpose of each playbook step | Exact lines, or both |
| Clips | Sized to the minutes, as in step 5 | A number per rep |
| Swaps | Two per clip (B and C) | None, or one |
| Clip length | 1 to 3 minutes | Shorter or longer |
| Leave out | Pricing and discount talk, private details, anything that would embarrass a rep or a buyer | More topics |
| Look for | Nothing set | A step the team is working on |

## Template

```markdown
# Game tape profile

Saved by the game-tape skill on {date}. Edit any line, or ask for a change in plain words.

## Meeting
- Meeting: {name}, {day and time}, run by {leader}
- In the room: {names}
- Game tape gets: {minutes} minutes
- Who's on tape: {every rep | my own calls, to teach | one rep, for a 1:1}

## Calls
- Recorder: {name}, reached through {the connector | exported files in {folder} | an API key named {KEY_NAME} in {file}}
- Link pattern: {such as <share link>?timestamp={seconds}, or "none, scrub to the time"}
- Reps:
  - {Name} <{the ID the recorder knows them by}>

## Playbook
- Playbook: {name and link or path | the built-in first-call playbook}
- Match: {purpose | exact lines | both}

## Settings
- Window: {last 30 days}
- Calls: {first calls with outside buyers, 15 minutes or longer}
- Clips: {sized to the minutes}
- Swaps: {two per clip}
- Clip length: {1 to 3 minutes}
- Leave out: {pricing and discount talk, private details}
- Look for: {nothing set}

## Notes from past runs
- {date}: {what the leader liked or changed, in their words, such as "match the job of a step, not the literal line"}

## Played
- {meeting date}: {rep}, {good or pause}, {account} {call date}, {start} to {end}
```

Save it in the project folder, not inside a run's work folder, so the next run finds it. Under Played, list each run's recommended clips, so the next run picks new moments. Keep the last eight meetings and drop older lines. Write settings as standing rules, such as "last 30 days", never one run's dates. Keep the notes short and dated. Add one only when the person says it should hold next time, or repeats the same change twice. Never put an API key in the profile, only the name of the file or setting that holds it.
