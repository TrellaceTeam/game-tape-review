# Contributing

Improvements are welcome, especially from people who run game tape with a recorder we haven't tested.

## Report a recorder that didn't work

Open an issue with the recorder, your plan on it, the assistant you used, and what went wrong. If a transcript export didn't convert, paste a few lines of it with the names and words changed, and keep the layout and the timestamps exactly as they were. That's all `tape.py` needs to learn a new layout.

## Share a link pattern

If your recorder has a "copy link at this time" option, run `python skills/game-tape/scripts/tape.py link "<the link>" <the time it showed>` and open an issue with the pattern it prints, with the call's ID replaced. We'll add it to [recorders.md](skills/game-tape/references/recorders.md).

## Keep examples fictional

Examples and tests use the fictional Fennick Software, its prospects and its people. Leave out real calls, real customers and anything private. A real transcript never goes in an issue or a pull request.

## What the script touches

`tape.py` reads and writes local files only. It uses no network and needs no key, so it runs in a chat app's sandbox and on a laptop alike.

## Run the checks

Run these from the repo root with Python 3.9 or later, using `python3` or `py` where that's the command. CI runs the same checks on every push and pull request.

```
python scripts/check_skill.py skills/game-tape
python scripts/lint_prose.py
python scripts/check_links.py
python -m unittest discover -s tests -v
python scripts/build_zip.py
```
