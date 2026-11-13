# md-reader

## What it is
A Claude Code plugin for macOS that makes Claude Desktop the viewer for Markdown files: double-click a `.md` file in Finder and it opens in the Files pane of a dedicated session, with no model call. Version 0.2.1, MIT.

## Where things are
- `handler/` — the Finder side. `handler.applescript` is the default app for `.md` files: it writes the file's path into a note named `_opening <file>` in `~/.claude/md-reader` and brings the session forward with a `claude://` link. `build.sh` compiles it into `~/Applications/md-reader.app`, sets its document types and icon, signs it ad hoc and registers it with Launch Services.
- `hooks/` — the Claude side. `register.ts` runs only in the session whose folder is `~/.claude/md-reader`. Once a second it looks for the note, checks the session is on screen (`get_layout`), hard-links the file into the folder, deletes the note and opens the link with `show_pane`. While a file is showing it re-links it when the original's size or date changes.
- `skills/` — `start` creates the dedicated session (Haiku, low effort) and hands it the install prompt; `install` builds the app and pins the session; `uninstall` removes both.
- `.claude-plugin/` — `plugin.json` and `marketplace.json`: the listing, version, icon and links.

## How to run it
- Install: `/plugin install md-reader --marketplace teajuw/md-reader`, then `/md-reader:start` in any Code session.
- Rebuild the Finder app by hand: `sh handler/build.sh`.
- Remove: `/md-reader:uninstall`.
- There are no tests. Checking it means double-clicking a Markdown file with Claude Desktop open.

## Tried and dropped
From the commit history, all on 2026-11-01:
- A `/read` command for opening files from inside a session. Removed; Finder is the only way in.
- Several reader sessions. Limited to one.
- History kept in `~/md-reader`. Moved to `~/.claude/md-reader`.
- A tracker, a suffix on linked file names, and copying files that live on another disk. All dropped; a file on another disk cannot be hard-linked.
- A setup page shown by the session, and the step in the start prompt that opened it.

## Parked
Nothing recorded in the repo.
