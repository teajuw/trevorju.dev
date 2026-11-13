---
name: add-project
description: Add a GitHub repo to the portfolio as a project. Use when Trevor says "add <repo>", "/add-project <repo>", or names a repo that should get a page on trevorju.dev.
---

# Add a project

The argument is a repo, as `owner/name` or a GitHub URL. Default owner: `teajuw`.

1. Confirm it can be a project: `gh api repos/<owner>/<name> --jq '.visibility'` must print `public`. If not, stop and say so.
2. Add it: `git submodule add https://github.com/<owner>/<name> projects/<name>`.
3. Confirm `projects/<name>/README.md` exists and starts with a `# ` title followed by one standalone sentence. If the README is missing or does not read as an article, say so and suggest `/article <name>`. Do not edit anything inside `projects/`: this site never writes to a project repo.
4. Write the first notes. There is no earlier pin to diff against, so read the repo once: its source, its commit log (`git -C projects/<name> log --format='%h %cs %s'`), and any `CLAUDE.md`, `AGENTS.md` or plan file it has. Write `notes/<name>/notes.md` with exactly these sections, as in `notes/md-reader/notes.md`:
   - `## What it is`
   - `## Where things are` (one line per top-level folder: path, then what it does)
   - `## How to run it`
   - `## Tried and dropped` (only what the history or files show; never guess a reason)
   - `## Parked`
5. Start `notes/<name>/log.md` with a `# <name> sync log` heading and one line:
   `YYYY-MM-DD  (new) → <short sha>  Added to the site. First notes written from a full read of the repo (<n> commits).`
6. Run `/check`.
7. Commit the submodule, `.gitmodules` and the notes folder together: `Add <name>`. Do not push; `/publish` does that.
