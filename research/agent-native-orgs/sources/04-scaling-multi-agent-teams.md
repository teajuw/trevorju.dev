# Safely scaling multi-agent teams with Claude Fable 5.2

- **URL:** https://claude.dev/blog/safely-scaling-multi-agent-teams-with-fable-5-2/
- **By:** Barry Zhang, Tianyi Peng, Elle Najt, Keller Scholl, Lance Martin
- **Published:** 2026-11-09.
- **Read:** 2026-11-13, full page.

The authors call it a toy experiment: one run, one task.

## Thesis

1,000 agents (one lead, 999 helpers) reproduced a formal Lean proof of Fermat's
Last Theorem in 28.7 hours using general tools, a shared database and git, with
no purpose-built platform and no researcher steering. The point is that a large
team can chase a long goal inside carefully designed safety boundaries.

## Mechanisms

- **Isolation.** One sandbox VM per agent: no internet, no credentials, no path
  to other sandboxes. A single shared machine broke down at about 100 agents.
- **Coordination with no messaging.** Agents coordinated only through a shared
  Postgres database and git. In the first 10 minutes the lead made five tables:
  - `Announce`: orders
  - `Assign`: who owns what
  - `Notes`: claims and progress
  - `Subtasks`: anyone adds one; the first to claim it owns it
  - `Landed`: the log of finished work
- **Permissions.** An agent can push only to its own branch and open a merge
  request into main. A separate job does the merge and refuses only on conflict.
- **Verification is mechanical.** A statement counts only when Lean's checker
  accepts the proof. No person approved individual merges.
- **Monitoring.** A classifier checks every tool call and blocks on failure. A
  person must review a block before the team restarts.

## Numbers

- 60 statements; 47 of them were judged infeasible early on, and all were proved.
- The task tree under the hardest statement grew to 2,418 tasks, 10 levels deep.
- By hour 30: 36,612 writes and 311,734 reads on the shared tables.
- More than a million tool calls; none blocked.
- Earlier run for comparison: a researcher plus dozens of agents, 11 days, about
  6 billion output tokens.

## Failure modes stated

- Agents lose track of project state without shared state to read.
- Agents "tend to give up on hard problems and misjudge their difficulty." The
  lead got 19 automatic reminders to keep going.
- Activity stalled near hour 18 and the run was restarted from its last save.
- "no single layer of defense is sufficient."

## Not in the page

Cost, merge-conflict rates, how much work was duplicated.
