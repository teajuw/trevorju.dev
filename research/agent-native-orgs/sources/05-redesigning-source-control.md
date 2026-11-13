# Redesigning source control at Anthropic

- **URL:** https://www.anthropic.com/research/redesigning-source-control
- **By:** Nick G. and the source control team (Anthropic Engineering)
- **Published:** 2026-10-13, updated 2026-10-15.
- **Read:** 2026-11-13, full page.

## Thesis

When agents write most of the code, the bottleneck becomes the developer
infrastructure built for human scale: source control, builds, CI. Git assumes
offline, decentralised clients; nearly all of Anthropic's clients are agents that
are always online. So they built Scion, a server-centric version control system,
and moved their monorepo off git in five months.

## Problems named

- Scale: about 25 million CI checkouts a day; main history near 100 GB.
- They were already using git as a centralised system with one authoritative copy.
- A merge queue is a global lock, and a global lock "doesn't make much sense at
  agent scale."

## Designs

- **No push.** "every commit, rebase, or merge happens on the server, so there's
  nothing to push."
- **Branches are discouraged.** Only main and release branches are meant to be
  long-lived refs, because every ref is global state all servers must agree on.
- **Test after merge, before deploy.** Changes can land while tests run and
  sometimes conflict; the agent usually fixes the conflict faster than a person
  would notice it. The gate sits in front of the deploy, not in front of main.
- **People review intent.** Team members "still review every change request ...
  but they now examine the intent of the change as opposed to reading every line
  of code." Approval rules can treat a comment-only change differently from a
  sensitive one.
- **Permissions per directory** inside the one repo.

## Numbers

- Merges per day: about 2,500 in May 2026, over 30,000 by September 2026.
- Seven people built it and migrated in five months.
- Infrastructure footprint 200x smaller than the git mirrors it replaced.

## Quotes

- "The bottleneck, now, is all of the developer infrastructure built for human scale: source control, builds, and CI."
- "The development lifecycle in Scion discourages refs (pointers to commits, such as branches and tags)"
- "What does CI even mean when hundreds or even thousands of changes can merge while tests are running?"
- "Scion is by no means a suitable replacement for git for general use."

## Limits stated

Only makes sense for enormous monorepos. Not offered publicly. Their token spend
is unusual.
