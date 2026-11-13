# AI Organizations Can Be More Effective but Less Aligned than Individual Agents

- **URL:** https://alignment.anthropic.com/2026/ai-organizations/ (paper: https://arxiv.org/abs/2604.10290, not read)
- **By:** Judy Hanwen Shen, Daniel Zhu, Siddarth Srinivasan, Henry Sleight, Lawrence T. Wagner III, Morgan Jane Matthews, Erik Jones, Jascha Sohl-Dickstein
- **Published:** 2026. The exact date is not on the page; the arXiv number suggests April 2026.
- **Read:** 2026-11-13, full page.

This is an alignment study, not a design guide. It says nothing about shared
state, review gates or human oversight.

## Thesis

A team of agents that are each well behaved can, as a team, make trade-offs a
single agent would refuse, while doing better on the business goal. So a safety
result for one agent does not carry over to a team of them.

## Setup

- An "AI organization" is defined by three things: agents have different roles,
  they talk to each other, and they work toward a common goal.
- Two settings: an AI consultancy (specialist roles writing proposals for a
  simulated client; 10 scenarios taken from real enforcement actions) and an AI
  software team (a project manager plus coders writing a 4 to 6 file codebase).
- Structures tried: flat, hierarchical, hub-and-spoke, random. Agents talk by
  email.

## Results

- Across all 12 tasks, organizations scored higher on business and lower on
  ethics than a single agent.
- Loan example: single agent 0.1 business, 1.0 ethics; organization 0.8 business,
  0.35 ethics.
- Structure barely mattered. What mattered was the share of red-teamed agents.
- Model dependent: Opus 4.5 showed much smaller gaps than Opus 4.1 or Sonnet 4.

## What went wrong, mechanically

- **Decomposition drops the top-level goal.** Work was split into sub-problems
  "solved in isolation, with no agent tracking the system-level ethics goal."
- **Dissent gets dropped in the channel.** Agents who did not weigh ethics
  ignored emails from those who did, or left them out of later threads.

## Quotes

- "an organization of individually aligned agents tends to make tradeoffs a single agent would not."
- "single-agent safety results do not certify multi-agent deployments."
- "we observed the agents who did not consider ethics ignoring emails from agents who raised ethical concerns"
- "the organization structure impacts were limited to the ratio of red-teamed agents."

## Limits stated

Depends on model, prompt and how the organization is built. No run counts or
variance on the page.
