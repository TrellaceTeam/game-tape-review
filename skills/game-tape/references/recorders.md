# Recorders

How to get calls and links out of each call recorder, read-only. Checked against vendor docs in October 2026. Vendors change menus and plans often, so when a step doesn't match what the person sees, follow what they see and say so in the hand-back.

## Pick the way in

1. **A connected recorder.** The session already has the recorder's tools, from a connector in Claude, an app in ChatGPT, or an MCP server in a coding agent. Use them to list calls, read titles and summaries, and shortlist. In a coding agent, also read the transcripts with them. In a chat app, ask for downloaded transcripts of the shortlisted calls, as step 3 of the skill explains.
2. **Exported files.** The person downloads each shortlisted call's transcript, with timestamps and speaker names on, and uploads the files or puts them in a folder.
3. **An API key, in a coding agent only.** The person stores the key in a file such as `.env` and tells you its name. Write a small client in the work folder that only sends read requests, and read the key inside it. Never print the key or ask for it in chat. Chat apps block outside network calls from code, so this route needs a coding agent on the person's own computer.

Whatever the route, use only the tools that read. Some connectors can also share, rename, move or delete. This skill never calls those, and the person can switch them off in the connector's settings.

A transcript without a time on each line can't make clips. Ask the person to export that call with timestamps on.

## Links that open at the right second

Each transcript's `LINK` header holds its own call's share link. Add a placeholder where the recorder takes a start time: `{seconds}` for whole seconds, `{ms}` for milliseconds, `{time}` for the 1m25s form, `{end}` for an end second.

When the table says "learn it", ask the person once to open any call, pause at some moment, use the recorder's "copy link at this time" option, and paste the link with the time the player showed. Then run:

```
python <skill>/scripts/tape.py link "<pasted link>" 12:34
```

It prints the pattern. Test it as [setup.md](setup.md#4-work-out-the-clip-links) says, then save it in the profile, so you never ask again. When it finds no time in the link, or the recorder has no such option, use each call's plain link, and the run sheet tells the leader where to scrub to.

## At a glance

| Recorder | Easiest way in | Time on each line | Share link field | Link at a second |
|---|---|---|---|---|
| Fathom | Connector or app. No file download, only copy | Yes in the API, check the connector | `share_url` | `<share_url>?timestamp={seconds}` |
| Fireflies | Connector or app. Downloads need Pro | Yes | `transcript_url` | Learn it from a line's link icon |
| Gong | Per-call download, or the API | Yes | `url` | `https://<your subdomain>.app.gong.io/embedded-call?call-id=<id>&from={seconds}&to={end}`, signed-in viewers only |
| Grain | Connector or app, or VTT download | Yes, ask for timestamps | `url` | None. Grain clips play without an account |
| Avoma | Custom connector (Organization plan or API add-on), or VTT download | Yes | `meeting_url` | None. Public snippets play without sign-in |
| Otter | Connector, or TXT export | Yes in exports | `url` | None. Snippet links play one passage |
| Read AI | Connector | Check | `report_url` | None documented |
| tl;dv <!-- prose-allow: semicolon --> | Connector (Pro). Copy only | Check | `url` | Learn it |
| Zoom | VTT download, or the connector | Yes in the VTT | `share_url` | None. Scrub, or upload the clip to Drive |
| Google Meet | Drive connector or the transcript doc | Only every 5 minutes | Drive file link | Learn it from Drive's "Copy link to this time" |
| Microsoft Teams | VTT or DOCX download, organizers only by default | Yes | The recording's link | None you can build. Scrub |
| Chorus | API | Yes | `url` | None documented |
| Granola | Connector | Clock times only | None | None. Granola keeps no audio |

## Fathom

- **Way in.** The Fathom connector in Claude or the Fathom app in ChatGPT. It sees the calls the person can see in Fathom. Fathom has no transcript download, only "Copy Transcript", so in a chat app the person pastes each shortlisted transcript into a text file and uploads it.
- **API.** Key under User Settings, API Access, on every plan. `GET https://api.fathom.ai/external/v1/meetings` with header `X-Api-Key`, filtered by `created_after`, `recorded_by[]=<rep email>` and `calendar_invitees_domains_type=one_or_more_external`, paged with `cursor`. Each meeting has `recording_id` and `share_url`. `GET /recordings/{recording_id}/transcript` returns lines with `speaker.display_name`, `text` and `timestamp` as HH:MM:SS. About 30 transcript reads a minute.
- **Link.** `<share_url>?timestamp={seconds}`. Fathom documents `?timestamp=` on its in-app call links, and we've used it on share links. Check one before the meeting. A share link opens without a login only when the call's sharing allows it, and some teams make viewers confirm their email.
- **Watch for.** Speaker labels are sometimes wrong. `matched_calendar_invitee_email` helps check who's who.

## Fireflies

- **Way in.** The Fireflies connector or app. `fireflies_get_transcript` returns each line as `[00:05 - 00:08] Speaker: text`. Filter calls with `fromDate`, `toDate` and `organizers`.
- **Export.** Pro plan and up: Download, Transcript, then JSON or SRT, with "Include timestamps" and "Include speaker labels" on. The free plan can't download.
- **API.** GraphQL at `https://api.fireflies.ai/graphql` with `Authorization: Bearer <key>`. The `transcripts` query lists calls with `transcript_url`, and `transcript(id:)` returns `sentences` with `speaker_name`, `text` and `start_time` in seconds.
- **Link.** Learn it. Fireflies copies a link from the link icon on any transcript line.
- **Watch for.** Unmatched speakers show as "Speaker 1". Summaries can get dates and owners wrong, so quote the transcript.

## Gong

- **Way in.** On a call, More actions, "Download transcript", for anyone with download permission. For many calls, the API. Gong's own connector returns summaries only, never transcripts.
- **API.** A Gong tech admin creates the key under Company Settings, Ecosystem, API. <!-- prose-allow: ecosystem --> Basic auth with the access key and secret, at the company's own base URL. `POST /v2/calls/extensive` lists calls (filter `fromDateTime`, `toDateTime`, `primaryUserIds`) and returns `parties` with each `speakerId`, name and `affiliation`. `POST /v2/calls/transcript` returns `sentences` with `start` in milliseconds and a `speakerId`. Convert with `--name "<speakerId>=<name>"` for each party.
- **Link.** `https://<your subdomain>.app.gong.io/embedded-call?call-id=<id>&from={seconds}&to={end}`. Viewers must be signed in to Gong with access to the call.

## Grain

- **Way in.** The Grain connector or app. Call `fetch_meeting_transcript` with `include_timestamps: true`, since timestamps are off by default. `list_meetings` filters by date and `participant_scope: external`.
- **Export.** Download transcript as VTT or SRT. Up to 20 meetings at once as Markdown.
- **Link.** No start-time link is documented. The leader can make a Grain clip for each pick, and clips play without a Grain account.

## Avoma

- **Way in.** Avoma's connector, added as a custom connector at `https://mcp.avoma.com/mcp`, on Avoma's Organization or Enterprise plan or with its API add-on. `get_meeting_transcript` returns speakers and timestamps.
- **Export.** Download, Transcript, as VTT.
- **API.** `GET https://api.avoma.com/v1/meetings/` with `from_date`, `to_date` and `is_internal=false`. `GET /v1/transcriptions/?meeting_uuid=<id>` gives each paragraph a `speaker_id` and word `timestamps` in seconds. Map speaker IDs to names from `speakers`.
- **Link.** None documented. A public snippet plays without sign-in, and the leader can make one per pick.

## Otter

- **Way in.** The Otter connector or app, or a TXT export. Export: the three dots, Export, TXT, with "Show speaker names" and "Show timestamps" on and the "combine paragraphs" options off. The free plan exports TXT only.
- **Link.** None documented. Snippet links play one highlighted passage.
- **Watch for.** Times can count from when the notetaker joined, or show the time of day when an admin turned that on. When `convert` warns that the first line looks like a time of day, convert again with `--zero`, and check one clip against the recording. The free plan stops transcribing at 30 minutes per call.

## Read AI

- **Way in.** The Read AI connector or plugin. `list_meetings` filters by date only. The API has no keys, so use the connector.
- **Watch for.** Video playback needs Read's Enterprise plans. Without it, the run sheet quotes the lines and the leader reads them out.

## tl;dv <!-- prose-allow: semicolon -->

- **Way in.** The tl;dv connector, on Pro and up. <!-- prose-allow: semicolon --> It reaches a call only when the call's organizer is also on a paid plan. By default it searches only calls the person attended, so ask it to include calls they weren't on. There's no file download, only a copy button.
- **Link.** Learn it.

## Zoom

- **Way in.** Cloud recording needs Zoom Pro or higher, with "Create audio transcript" turned on before the call, or there's no transcript. Download the "Audio transcript" VTT from Recordings and Transcripts, Cloud recordings. The Zoom connector in Claude or ChatGPT also needs an admin's approval and Smart Recording or Meeting Summary on, and developers have reported it failing to fetch transcripts, so prefer the VTT.
- **Link.** Zoom recording links can't open at a time. Give the share link and the time to scrub to. For a clip that has to play from a link, the leader can download the recording and upload it to Google Drive or Loom.

## Google Meet

- **Way in.** Meet saves each transcript as a Google Doc in the organizer's Drive, in the Meet folder, on Business Standard and higher. The Drive connector reads it, or the person downloads it. The doc marks the time only every 5 minutes, so clip times are accurate only to about 5 minutes. Say so in the run sheet, and tell the leader to find the moment by its words.
- **Link.** Recordings play in Drive. Learn it from "Copy link to this time" beside Share in Drive's player.

## Microsoft Teams

- **Way in.** In the meeting's chat: Recap, Transcript, Download, as VTT or DOCX. By default only organizers and co-organizers can download. Automated routes need a Microsoft admin.
- **Link.** The player's "Copy link at current time" hides the time inside an encoded value, so `tape.py link` can't learn it. Keep the run sheet on the plain recording link and the time to scrub to. After the run, the leader can copy a link at each clip's start by hand.

## Chorus

- **Way in.** The API, with a personal token from Personal Settings. `GET https://chorus.ai/v3/engagements` lists calls. `GET /api/v1/conversations/{id}` returns `utterances` with `speaker_name`, `snippet` and `snippet_time` in seconds. The ZoomInfo connector summarizes and costs credits.
- **Link.** None documented.

## Granola

- **Watch for.** Granola deletes the audio after it transcribes, and its transcripts carry clock times. There's no recording to link to. The run sheet can still quote the moments, and the leader reads them out.

## Any other recorder

1. Look for a connector in the chat app's directory, or an MCP server in the recorder's docs.
2. Otherwise export a transcript with timestamps and speaker names on, as VTT, SRT, DOCX, JSON or TXT, and convert it. When the converter can't read it, it says why.
3. Learn the link from one copied "link at this time".
