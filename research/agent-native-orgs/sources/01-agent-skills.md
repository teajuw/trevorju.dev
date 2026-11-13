# Equipping agents for the real world with Agent Skills

- **URL:** https://www.anthropic.com/research/equipping-agents-for-the-real-world-with-agent-skills
- **By:** Barry Zhang, Keith Lazuka, Mahesh Murag (Anthropic Engineering)
- **Published:** 2025-10-16. A note dated 2025-12-18 says Agent Skills became an open standard (agentskills.io).
- **Read:** 2026-11-13, full page.

## Thesis

A general agent gets domain expertise from folders of instructions it finds and
loads on demand, so one agent can be specialised without building a custom agent
per job.

## Mechanisms

- A skill is a directory with a `SKILL.md`. The file opens with YAML frontmatter:
  `name` and `description` are required. It may bundle other files and scripts.
- **Progressive disclosure, three levels.** (1) Every installed skill's name and
  description are in the system prompt from the start. (2) The agent reads the
  full `SKILL.md` only when the skill looks relevant. (3) Linked files are read
  only when needed.
- **Code in skills.** A bundled script can be run without loading it into
  context. Code is deterministic and repeatable where generating tokens is not.
- **Authoring advice.** Start from evaluation: run the agent on real tasks and
  write skills for the gaps you see. Treat name and description as the trigger.
  Ask the agent to write its successes and mistakes back into the skill.
- **Security.** Install only from trusted sources; audit bundled files.

## Quotes

- "organized folders of instructions, scripts, and resources that agents can discover and load dynamically"
- "provides just enough information for Claude to know when each skill should be used"
- "the amount of context that can be bundled into a skill is effectively unbounded."
- "Building a skill for an agent is like putting together an onboarding guide for a new hire."
- "letting them codify their own patterns of behavior into reusable capabilities."

## Not in the page

No numbers. Nothing on versioning, ownership of shared skills, or how
description-based triggering holds up with many skills. Nothing on agents
sharing work with each other; only a hope that agents will one day write and
evaluate skills themselves.
