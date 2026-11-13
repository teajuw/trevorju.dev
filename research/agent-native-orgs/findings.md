# Findings

Numbers in brackets point to the notes in `sources/`. "07.9" means item 9 in
the wider search.

## What the sources agree on

### 1. The slow part moved from making to checking

Every engineering source says the same thing in its own words. Writing is
cheap; verification, review, builds and CI are the bottleneck [03, 05, 07.7].
One person can only land one significant change at a time [07.7].

### 2. Agents coordinate through shared state, not by talking

The 1,000-agent run had no messaging at all. Agents coordinated through five
database tables and git: orders, ownership, notes, subtasks, and a log of
finished work [04]. Cursor's workers never talk to each other [07.2, 07.3].
Gas Town keeps tasks and notes in a git-backed ledger [07.4]. When agents did
coordinate by message, in the AI organizations study, the messages that raised
concerns were the ones that got ignored [02].

### 3. Isolate each change, then integrate mechanically

One sandbox, worktree or fresh checkout per agent [04, 07.1, 07.3, 07.7]. An
agent pushes only to its own branch; a separate job merges [04, 07.4]. Locks
and hand-coordination failed [07.2].

### 4. Trunk plus a preview per change. Nobody runs a long-lived dev branch

No source recommends a standing `dev` branch. Anthropic's own system discourages
branches other than main and release branches [05]. DORA's guidance is three or
fewer active branches, merged daily [07.13]. What teams run instead is an
environment per change: an app instance per worktree [07.1], a preview URL per
commit, tested by a browser agent on the live URL [07.10].

### 5. The gate sits in front of the deploy, not in front of main

Anthropic tests after merge and before deploy, and accepts that main is briefly
wrong [05]. Cursor accepts a small steady error rate and cleans up to a green
branch [07.3]. The check that matters is mechanical where it can be: the proof
counted only when the checker accepted it [04].

### 6. People review intent and taste

Human review is kept for legal risk, trust boundaries, security, and product
sense and taste [03]. Reviewers "examine the intent of the change as opposed to
reading every line" [05]. About 80% of human effort goes to planning and review
[07.5]. Agents are weakest exactly where this site is most exposed: visual
design and ambiguous work [07.12].

### 7. Know-how lives in the repo, and the always-loaded part is a short index

Skills carry procedures [01]; a plugin of skills replaced a six-week ramp for
new sales reps [06]. Lessons from each bug are written back so every agent
inherits them [07.5]. The entry file should be a table of contents, about 100
lines, pointing into the docs [07.1].

### 8. A skill that has to be chosen often is not chosen

The one measured result on this: a skill was never invoked in 56% of cases and
did no better than no documentation, while an always-loaded index scored 100%
[07.9]. Skills load only a name and description up front, and that description
is the whole trigger [01].

### 9. A team of well-behaved agents can still drift as a team

Work split into sub-problems was "solved in isolation, with no agent tracking
the system-level" goal [02]. Structure barely changed this. The recurring
smaller failures: claiming "done" early [07.3], giving up on hard problems and
misjudging difficulty [04], and following vague instructions to the end [07.3].

## Where they disagree

- **Is human review required?** Optional at OpenAI [07.1]; required per
  Cognition and Willison [07.12, 07.7]; "where it matters" at Anthropic [03].
  It tracks the stakes and how mechanical the check is.
- **Merge queue or free-for-all?** Gas Town serialises merges [07.4]; Cursor
  removed its integrator [07.2]; Anthropic calls a global lock senseless at
  agent scale [05]. The free-for-all cases are either greenfield or enormous.
- **Who approves production?** Under-documented everywhere. The Vercel posts do
  not say [07.10].

## What this means for the portfolio

The portfolio already is a small agent native org: sessions in project repos
are the workers, the portfolio repo is the shared state, and Trevor is the
overseer. Reading the sources against it:

### Already matching

| What the sources do | What the portfolio has |
|---|---|
| Shared state instead of messaging [04] | Pins, `notes/<name>/notes.md`, and `log.md`. The log is the same idea as the `Landed` table. |
| A fresh checkout per worker [07.7] | Skills work in `~/.claude/portfolio/trevorju.dev`, not in the session's repo. |
| Mechanical verification [04, 07.10] | `build.py --check` and the browser check in `shots.py`. |
| Know-how shipped as a plugin [01, 06] | The private `portfolio` plugin. |
| Lessons written back [07.5] | "Tried and dropped" in the notes; `ARTICLES.md`. |
| Machine-readable twin [07.13] | `/<slug>.md`, `llms.txt`. |

### Gaps the research points at

1. **Today's stray deploy is finding 8, exactly.** A session asked to add a
   project never chose the skill and went to the old repo. Sharper descriptions
   help, but the measured fix is passive context: something always loaded that
   says where the portfolio is. Candidates: a line in each project repo's
   `CLAUDE.md` or `AGENTS.md`, added by `/portfolio:add-project`; a line in the
   global `CLAUDE.md` per machine.

2. **Dev and prod: the evidence is against a `dev` branch and for previews.**
   The backlog asks whether to add a `dev` branch or use `trevorju.com` as prod.
   Finding 4 says neither is what agent-heavy teams run. They keep one trunk
   and give every change its own preview, checked on its live URL, and put the
   gate in front of the deploy (finding 5). Translated: a session opens a pull
   request instead of pushing to main; the pull request gets its own preview
   URL; `shots.py` runs against that URL and its screenshots land on the pull
   request; merging is the promotion. A second domain is useful as the host for
   previews, not as a second standing environment. GitHub Pages does not do
   per-change previews on its own, so this is a hosting decision.

3. **Sessions push straight to main.** Every source that isolates work also
   limits a worker to its own branch plus a merge request [04, 07.4]. Today
   `/portfolio:publish` pushes main from whichever session runs it. With one
   project this is fine. With several sessions posting, it is the first thing
   that breaks.

4. **Nobody owns the site-level goal.** Each project's session writes its own
   article and wants it to look good. Finding 9 says that is how a team drifts:
   every part is fine and the whole is not. For a portfolio the whole is
   honesty of claims and coherence across articles. `ARTICLES.md` and `/check`
   cover form. Nothing reads a new article as a sceptical outsider before it
   goes live. The approval step is where Trevor's taste belongs (finding 6),
   and it should show intent: what changed, why, and the screenshots.

5. **No record of work in flight.** The 1,000-agent run had `Assign` and
   `Subtasks` as well as `Landed` [04]. The portfolio only has the log of what
   landed. Open pull requests would be that record for free.

6. **"Done" is not explicit.** Agents claim done early [07.3] and completion
   should be an explicit signal [07.6]. `/portfolio:publish` checks the live
   site, which is right; a posting session should end with the preview URL and
   screenshots, not a sentence.

### What does not apply

Scale. Anthropic's source control work is for a repo with 30,000 merges a day
and says plainly it is not a general replacement for git [05]. The 1,000-agent
sandboxing is for untrusted agents at volume [04]. The portfolio has one person
and a handful of sessions. The ideas that transfer are the cheap ones: shared
state, isolation per change, a preview per change, a mechanical check, and a
person approving intent.

## Open questions for the next pass

- Which host gives a preview URL per pull request with the least machinery?
- Should project repos carry a pointer file, and who keeps it current?
- What would an "editor" check read for, and can it be scored?
- Would a public feed of what agents posted (the log, rendered) be worth having
  on the site itself?
