---
name: sync
description: Bring each project on the portfolio up to its latest commit and update its notes from the diff. Use when Trevor says "/sync", "sync the projects", or has pushed to a project repo and wants the site to pick it up.
---

# Sync projects

The pin (the commit each submodule points at) is the bookmark: the notes were true as of that commit. Read only what changed since. Never reread a whole repo here.

1. `git pull --ff-only` in this repo first, so another machine's sync is not repeated.
2. For each folder under `projects/`:
   1. `old=$(git -C projects/<name> rev-parse --short HEAD)`
   2. `git -C projects/<name> fetch origin` then `new=$(git -C projects/<name> rev-parse --short origin/HEAD)`
   3. If `old` equals `new`, the project is current. Say so and move on.
   4. Read the change, smallest first: `git -C projects/<name> log --format='%h %s' $old..$new`, then `git -C projects/<name> diff --stat $old..$new`. Open the full diff only for files that could change a line of the notes.
   5. Update `notes/<name>/notes.md`. Match the changed paths against "Where things are" and edit only the sections those changes touch. A removed feature goes under "Tried and dropped" with what the commit message says about it and nothing more. Leave untouched sections exactly as they are.
   6. If the diff is too large or too tangled to update the notes from it honestly, do not guess: say the notes need a full reread and ask before doing one.
   7. Add one line directly under the heading of `notes/<name>/log.md` (newest first):
      `YYYY-MM-DD  <old> → <new>  <what changed, in a few words>. Notes: <sections edited, or "no change">.`
   8. Move the pin: `git -C projects/<name> checkout --quiet $new`.
3. Run `/check`.
4. Commit the moved pins, the notes and the log lines together in one commit: `Sync <names>`. Do not push; `/publish` does that.
5. Tell Trevor, per project, what came in and which notes sections changed.

Never commit or push inside `projects/<name>`.
