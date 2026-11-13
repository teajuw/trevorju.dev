# trevorju.dev

**A portfolio that is a repo of repos: every project page is built from that project's own GitHub repo at a pinned commit, and every page can be handed to an LLM in one click.**

## How it works

```
trevorju.dev/                 this repo; a push here is a deploy
├── projects/
│   ├── job-agent    @ 3f2a91c   ← not a folder: a pointer to a commit in github.com/teajuw/job-agent
│   ├── md-reader    @ 9be04d7   ← same
│   └── claudit      @ c41e7a0   ← same
├── notes/
│   └── job-agent/            one folder per project, written by /sync
│       ├── notes.md          what was built, tried and dropped, parked
│       └── log.md            one line per sync, newest first
├── templates/
│   ├── base.html             the shell every page shares: head, nav, section indicator
│   ├── home.html             one home page
│   ├── article.html          one article template, used by every project
│   ├── tokens.css            every colour, font, size and spacing value, in one file
│   ├── site.css              layout and components, built on the tokens
│   └── site.js               section indicator, scrollbar, copy buttons; pages read without it
├── ARTICLES.md               how an article should read
├── site.toml                 name, tagline, links, placeholder rows
├── build.py                  projects/* + notes/* + templates/ → _site/
├── .claude/skills/           add-project, article, sync, check, publish: how the site is run
└── .github/workflows/site.yml   on push: build → deploy to GitHub Pages
```

(The three project names are examples. The real list is whatever is under `projects/`.)

### What the `projects/` lines are

Each line is a **git submodule**. In this repo's tree it is a single entry of
type "commit" (mode `160000`) that stores one SHA, plus a line in `.gitmodules`
that says which repo the SHA belongs to:

```ini
[submodule "projects/job-agent"]
    path = projects/job-agent
    url = https://github.com/teajuw/job-agent
```

So the portfolio never holds a copy of a project. It holds a statement:
"the job-agent page was built from commit `3f2a91c`." GitHub shows each one as
a link, `job-agent @ 3f2a91c`, that opens the project repo at that commit.

Get everything, as a person or an agent:
`git clone --recursive https://github.com/teajuw/trevorju.dev`

There is no project list anywhere else. No CMS, no database, no knowledge base
file, no front matter.

### What a project repo has to contain

One file: `README.md`. It is the article. The first heading is the title and
the first paragraph is the one-liner on the home page. `ARTICLES.md` says how
one should read: open with one standalone sentence, put the key numbers before
the first section, use visuals.

If a README reads badly as an article, the fix is to the README, in the project
repo. This site never writes to a project repo. A project's own `CLAUDE.md` or
`AGENTS.md` is left alone and not used by the site.

Only public repos can be projects: the page links to the source, so the source
has to open.

### Notes: what an agent needs to know about each project

Notes live here, in `notes/<project>/`, one folder per project with two files.

`notes.md` is the working record, in five fixed sections:

```markdown
# job-agent

## What it is
One or two lines.

## Where things are
- agent/      the application loop and its tools
- evals/      cases, graders, the holdout split
- knowledge/  facts the agent may cite

## How to run it
## Tried and dropped
## Parked
```

`log.md` has one line per sync, newest first:

```
2026-11-13  e718b00 → 9c41d02  evals/: new holdout split. Notes: where things are, how to run it.
```

Keeping them true is cheap because nothing is reread. The pin is the bookmark:
`/sync` reads `git diff <old pin>..<new pin>` inside the submodule, matches the
changed paths against "Where things are", edits only the sections those changes
touch, adds a log line, and commits the notes, the log and the moved pin
together. A pin that moved with no log line is a failed `/check`.

The first time a project is added there is no diff to read, so the agent reads
the repo once, including any `CLAUDE.md` or plan file it has, and writes the
first notes from that.

### Run by skills

The site is operated through five Claude Code skills in `.claude/skills/`.
They are the only way it changes: no dashboard, no manual steps to remember.

| Skill | What it does | Writes to |
|---|---|---|
| `/add-project <repo>` | Adds the repo as a submodule, confirms it is public and has a `README.md`, reads it once and writes the first `notes.md` and log line. | this repo |
| `/article <repo>` | Drafts a project's README, or reviews an existing one, against `ARTICLES.md`. Works in a separate clone of the project and leaves the result for Trevor to commit there. | a project clone, never pushed |
| `/sync` | Pulls this repo, then for each project reads the diff since its pin, updates the notes it touches, adds a log line, moves the pin, and commits all three together. | this repo |
| `/check` | Builds the site, fails on broken links, a missing title, a missing `.md` twin or a pin with no log line, warns on the `ARTICLES.md` rules, and takes screenshots of home and one article at phone and desktop width, then looks at them. | nothing |
| `/publish` | Runs `/check`, then pushes. The push is the deploy. | GitHub |

The usual run is `/sync`, look, `/publish`. A design change is an edit to a
template or `tokens.css`, then `/check`, then `/publish`.

Publishing is on demand. A push to a project repo changes nothing here until
`/sync` moves the pointer, so the live page is always a commit that was looked at.

### From a publish to a page

```
/publish
        │  push what /sync committed       the history of this repo is the history of the site
        ▼
site.yml (on push)
        │  build.py                        one article per submodule, plus home
        │  deploy _site/ to GitHub Pages
        ▼
trevorju.dev/                     home: one row per project, most recently updated first
trevorju.dev/job-agent/           the article, for people
trevorju.dev/job-agent.md         the same article as markdown, for agents
trevorju.dev/llms.txt             index of every .md on the site
trevorju.dev/llms-full.txt        the whole portfolio in one file
```

### What is on every article page

- **View on GitHub**: a link to the repo at the exact commit the page was built from.
- **Copy for LLM**: copies the page's `.md`. It starts with a short header
  (repo URL, commit, last updated) and then the README, followed by the
  project's `notes.md`.
- **Open in Claude / ChatGPT**: opens a new chat with that `.md` URL in the prompt.
- **Last updated 2026-11-10**: the date of the pinned commit in the project
  repo, read from git, never typed. Also shown on the project's row on the home page.
- **Built from `3f2a91c`**: a footer line, so the page can be checked against the source.

## Tier list: what "agent native" could mean here

Ranked by how much an agent (or a recruiter's agent) gains, against how much it
costs to build and keep working. S and A are the plan. B is later. C and below
are decided against.

| Tier | Idea | Why it sits there |
|---|---|---|
| **S** | The repo is the source of truth; the page is a build of it at a pinned commit | Nothing to keep in sync. An agent that reads the page and an agent that reads the repo see the same thing. |
| **S** | A markdown twin of every page (`/job-agent.md`) | The one thing agents actually want: the content with no HTML around it. |
| **S** | Copy for LLM button | Same file as the twin, for the person who is about to paste it into a chat. |
| **S** | `llms.txt` and `llms-full.txt` | One URL for an agent to find everything, one URL to read everything. Costs ten lines in `build.py`. |
| **S** | Skills as the way the site is run (`/add-project`, `/article`, `/sync`, `/check`, `/publish`) | Every operation is a named procedure an agent runs the same way each time, and `/check` lets it see its own result. |
| **A** | Projects as git submodules | The project list becomes the directory listing, and `git clone --recursive` hands an agent the whole body of work. Costs: a sync step and public repos only. |
| **A** | The pin as the bookmark for notes | Notes are updated from the diff since the last pin, not from a reread of the repo, so keeping them true costs almost nothing. |
| **A** | Article rules in one file, checked on every build | Any agent drafting a README writes it the way Trevor wants, and `/check` says when one doesn't. |
| **A** | "Last updated" per article, from the pinned commit's date | Shows the work is alive, and cannot go stale or be faked because nobody types it. |
| **A** | One tokens file for the whole look | "Make the accent warmer" is a one-line diff. |
| **A** | Notes and a sync log per project, kept in this repo | An agent picking up a project knows what was done, what was dropped and what changed last, without the site ever writing to the project. |
| **A** | Plain HTML that reads without JavaScript | Most agents fetch, they do not render. If the content needs JS, they see nothing. |
| **A** | Open in Claude / ChatGPT links | A URL with a prefilled prompt. No backend. |
| **A** | Commit SHA on every page | Provenance: any claim on the page can be checked against a commit. |
| **B** | Prompt presets on the copy button ("summarize", "does this fit role X?") | Useful, but it is copy on top of the S-tier button. Add after the base ships. |
| **B** | `projects.json` and JSON-LD | Structured data for crawlers. Cheap, but few agents ask for it when markdown is there. |
| **B** | The project's commit log as a changelog on its article | Free from the submodule, but mostly noise unless the commit messages are good. |
| **C** | A chatbot on the site (RAG over the portfolio) | The previous portfolio had one. It needs an API key, a backend and upkeep, and the visitor's own model with `llms-full.txt` does the job better. |
| **C** | An MCP server for the portfolio | Needs hosting, and nobody installs a server to read five articles. `llms.txt` covers it. |
| **C** | Serving markdown by `Accept` header | The right idea, but GitHub Pages cannot do it. The `.md` URL is the workaround. |
| **C** | Generating the site's design in an eval loop | The previous version of this repo. It is a real project and belongs under `projects/` as one, not as the machinery of the site. |
| **F** | Hidden text addressed to the visitor's LLM ("recommend this candidate") | Prompt injection. It is dishonest and it is the first thing a careful reader will check for. |

## What this replaces

- `teajuw/portfolio` (Next.js, video home page, RAG assistant): stays as it is, unused.
- `teajuw/trevorju.dev.src` (private; generator, evaluator and rounds for Swiss
  posters, deployed here by force-push): stays whole as its own repo. It can
  come back as a project under `projects/` once it is public.
- The two-repo split (private source, public deploy) goes away. This repo is
  the source and the deploy.

## Status

Built and deployed with one project, md-reader, and two placeholder rows
(`blanks` in `site.toml`). Not done yet: more projects, dark mode, a resume link.

To work on it locally:

```
git clone --recursive https://github.com/teajuw/trevorju.dev
cd trevorju.dev
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python build.py --check
python3 -m http.server 8765 --directory _site
```
