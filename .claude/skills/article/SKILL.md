---
name: article
description: Draft or review a project's README as a portfolio article, against ARTICLES.md. Use when Trevor says "/article <repo>", asks to write up a project, or asks whether a README is ready for the site.
---

# Draft or review an article

A project's `README.md` is its article. Read `ARTICLES.md` at the root of this repo before anything else; its rules are Trevor's and they win over your own taste.

This site never writes to a project repo, so work in a separate clone of the project (ask where it is, or clone it outside this repo). Never edit files under `projects/`.

## Review (a README exists)

1. Read the README and check it against each rule in `ARTICLES.md`.
2. Report, rule by rule, what passes and what does not, quoting the lines in question.
3. Propose the smallest edits that fix it. Show them as a diff. Apply them in the project clone only if Trevor says yes.

## Draft (no README, or Trevor asks for a rewrite)

1. Read the project: source, commit log, any notes or plan files, and `notes/<name>/notes.md` here if it exists.
2. Ask Trevor for what the repo cannot tell you: why he built it, and the numbers that show it worked. Do not invent a number, a result or a motive. If there is no measured result yet, say so and leave the number out.
3. Write the README in the project clone: title, one standalone sentence, the key numbers, an early visual, then the sections the project needs.
4. For a visual, prefer a real screenshot or a diagram of how it works. Give every image alt text that says what it shows.

## Either way

Leave the result uncommitted in the project clone and tell Trevor which file changed. He commits and pushes it there; `/sync` then brings it onto the site.
