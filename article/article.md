# trevorju.dev

A portfolio that is a repo of repos.

Every project page is built from that project's own GitHub repo at a pinned commit, and can be handed to an LLM in one click.

## Why

The previous version of this site designed itself. A generator wrote a page, an evaluator graded it against written criteria, and the loop ran round after round. It was a real project and a poor portfolio: the note that parked it reads "the whole loop feels random and unclear; simplify soon." The site before that had a chatbot that answered questions about the work.

Both put the effort in the wrong place. The people and the models reading a portfolio want the same thing: the work itself, stated plainly, with a way to check it. So this version has one idea. The portfolio does not describe projects; it points at them.

## How it works

Each project is a git submodule. In this repo it is not a folder of code but a single line that names a repo and a commit. The page for a project is built from that repo at that commit, so every page can say exactly what it was built from, and the "last updated" date is the date of that commit, read from git and never typed.

A project's page comes from one Markdown file in its own repo, `article/article.md`. It opens the same way every time: a title, one standalone sentence, the numbers that matter, a picture. The rules are written down once, in `ARTICLES.md`, so any session can write one.

What an agent needs to know about a project lives here, in two small files per project: notes on what was built and what was dropped, and a log with one line per update. They are kept true cheaply. When a project moves, only the diff since the pinned commit is read, and only the notes those changes touch are edited.

## What makes it agent native

- **A markdown twin of every page.** Add `.md` to a page's address and you get the article and its notes with no HTML around them.
- **Copy for LLM.** One button copies that twin. Selecting any passage offers to copy it with its source and commit.
- **`llms.txt` and `llms-full.txt`.** One address to find everything, one to read everything.
- **Pages that read without scripts.** Most agents fetch a page; they do not run it.
- **Run by skills.** Adding a project, writing its article, syncing, checking and publishing are each a named skill, so the session that just finished a piece of work can write it up while it still knows why things were done.

## What was dropped

- **The chatbot.** It needed a key, a backend and upkeep, and a visitor's own model reading `llms-full.txt` does the job better.
- **An MCP server for the portfolio.** Nobody installs a server to read a handful of articles.
- **Generating the design in an eval loop.** That is a project, not the machinery of a site.
- **The README as the article.** A README says how to use a repo; an article says what the project is and what it achieved.
- **Notes inside each project's `CLAUDE.md`.** That file holds instructions for working in the repo, and mixing history into it meant the site had to write to every project.

## Not done yet

There is one project besides this one, no dark mode, and the home page still shows placeholder rows.
