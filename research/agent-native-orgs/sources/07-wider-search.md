# Wider search: 13 more sources

Gathered 2026-11-13 by a research subagent. Each page was opened unless marked.
Quotes were extracted by a fetch tool from the live page: spot-check any quote
before publishing it.

Three gaps: the OpenAI post was read through a mirror (openai.com returned 403);
Gas Town was read from its GitHub README (the Medium post returned 403); the
DORA 2025 report was seen only through secondary coverage.

## 1. Harness engineering: leveraging Codex in an agent-first world
Ryan Lopopolo, OpenAI, 2026-02-11. https://openai.com/index/harness-engineering/ (read via mirror)

- About 1M lines and 1,500 merged PRs in five months with no hand-written code; 3 to 7 engineers.
- The app boots per git worktree, so every change has its own running instance. Agents take DOM snapshots and screenshots and read that instance's logs.
- `AGENTS.md` is about 100 lines and is a map into a structured `docs/` folder. Linters and CI enforce the conventions.
- PRs are short-lived; review is mostly agent to agent; human review is optional.
- Background agents open small clean-up PRs against "golden principles" kept in the repo.
- "instead of treating `AGENTS.md` as the encyclopedia, we treat it as the table of contents."
- "corrections are cheap, and waiting is expensive."
- Critique (Birgitta Böckeler, martinfowler.com, 2026-04-02): "This approach puts a lot of faith into the AI-generated tests, that's not good enough yet."

## 2. Scaling long-running autonomous coding
Wilson Lin, Cursor, 2026-01-14. https://cursor.com/blog/scaling-agents

- Hundreds of agents on one project.
- Shared-file locking failed. A flat structure made agents risk-averse: nobody owned the hard problems.
- What worked: planners, workers who do not coordinate with each other, and a judge per cycle.
- A dedicated integrator for conflicts became a bottleneck and was removed.
- "Twenty agents would slow down to the effective throughput of two or three, with most time spent waiting."

## 3. Towards self-driving codebases
Wilson Lin, Cursor, 2026-02-05. https://cursor.com/blog/self-driving-codebases

- Each worker has its own copy of the repo and hands off to the planner that asked. Workers never talk to each other.
- Requiring 100% green before every commit serialised everything. They accept a small steady error rate and run a periodic clean-up to a green branch.
- Failure modes: premature "done" claims; agents chasing obscure features from vague instructions.
- "Agents have immense engineering skill but will follow instructions to the end, good or bad."

## 4. Gas Town
Steve Yegge, 2026-01-01. https://github.com/steveyegge/gastown

- Roles: a human Overseer, a Mayor that dispatches, workers in isolated worktrees, Witnesses that nudge stuck agents, a Refinery that merges.
- The Refinery is a serialised merge queue. Workers never push to main.
- Beads: a git-backed ledger holding tasks, merge requests and agent notes as structured data.
- Criticism (Bill de hÓra): favours progress over correctness; confident wrong results.

## 5. Compound Engineering: How Every Codes With Agents
Dan Shipper and Kieran Klaassen, Every, 2025-12-11. https://every.to/chain-of-thought/compound-engineering-how-every-codes-with-agents

- Loop: plan, work, assess, compound. Five products, each run mainly by one person.
- Agents test as a user through Playwright.
- The "compound" step writes lessons from bugs and reviews back into the repo or plugins, so every agent inherits them.
- "Roughly 80 percent of compound engineering is in the plan and review parts, while 20 percent is in the work and compound."

## 6. Agent-native Architectures
Dan Shipper and Claude, Every. https://every.to/guides/agent-native

- Parity: the agent can do anything the UI can. Files are the shared interface.
- Agent and person share one workspace, so the person can inspect and change what the agent made.
- "Agents need an explicit way to say "I'm done." Don't detect completion through heuristics."

## 7. Embracing the parallel coding agent lifestyle
Simon Willison, 2025-10-05. https://simonwillison.net/2025/Oct/5/parallel-coding-agents/

- Isolation by fresh checkout rather than worktree.
- "I can only focus on reviewing and landing one significant change at a time"
- "Code that started from your own specification is a lot less effort to review."

## 8. Ralph Wiggum as a "software engineer"
Geoffrey Huntley, 2025-07-14. https://ghuntley.com/ralph/

- One agent, one repo, one task per loop. State lives in files: `specs/`, a prioritised `fix_plan.md`, and a short `AGENT.md` of learnings.
- Tests and type checks after every change are the backpressure.

## 9. AGENTS.md outperforms skills in our agent evals
Jude Gao, Vercel, 2026-01-27. https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals

- Baseline 53%; skill 53%; skill plus explicit instructions to use it 79%; an always-loaded docs index 100%.
- The skill was never invoked in 56% of cases.
- The index was cut from about 40 KB to 8 KB with no loss: it points to files instead of inlining them.
- "Without those instructions, skills performed no better than having no documentation at all."

## 10. Agentic Infrastructure, and the General Intelligence case study
Vercel, 2026-04-09 and 2026-05-04. https://vercel.com/blog/agentic-infrastructure · https://vercel.com/blog/how-general-intelligence-used-agents-to-build-an-agent-platform-on-vercel

- Over 30% of Vercel deployments were started by agents in April 2026; a later update says over 50%.
- Immutable deploys, a preview URL per commit and instant rollback are called "absolute prerequisites for machine-driven software development".
- General Intelligence: 8 people, about 100 live previews at once, 10 PRs per engineer per day, no local development. A browser agent tests every preview on its live URL.
- Neither post says who approves promotion to production.

## 11. Introducing Agent Readiness
Factory, 2026-01-20. https://factory.com/news/agent-readiness

- Over 60 criteria in 8 pillars; five levels.
- "The agent is not broken. The environment is."

## 12. Devin's 2025 Performance Review
Cognition, 2025-11-14. https://cognition.com/blog/devin-annual-performance-review-2025

- PR merge rate rose from 34% to 67%.
- Strong on verifiable, well-scoped work. Weak on ambiguous projects and on visual design.
- "Human review is still necessary, because code quality is not straightforwardly verifiable."

## 13. Standards
- **agents.md** (https://agents.md/): used by over 60k open-source projects; the nearest file in the tree wins.
- **llms.txt** (Jeremy Howard, 2024-09-03, https://llmstxt.org/): a markdown index plus a `.md` twin per page.
- **GitHub Agent HQ** (2025-10-28, https://github.blog/news-insights/company-news/welcome-home-agents/): a mission control for assigning and watching agents; one branch and one PR per task.
- **DORA** (https://dora.dev/capabilities/trunk-based-development/): "Have three or fewer active branches" and "Merge branches to trunk at least once a day."
