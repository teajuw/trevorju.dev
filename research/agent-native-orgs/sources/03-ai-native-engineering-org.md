# Running an AI-native engineering org

- **URL:** https://claude.com/resources/articles/running-an-ai-native-engineering-org
- **By:** No byline. Written up from a talk by Fiona Fung, Director of Engineering for Claude Code and Claude Cowork, at Code w/ Claude SF 2026.
- **Published:** 2026-06-03.
- **Read:** 2026-11-13, full page.

An experience report from one team. No comparison data and no failure cases.

## Thesis

Once agents write the code, the slow part is no longer writing it. It is
verification, review and security. Processes built around the cost of typing
code stop fitting, so the team rewrote planning, review, structure and metrics.

## Practices

- **Planning is just in time.** A six-month roadmap was stale by month three.
  Planning moved from design docs to discussion in PRs and prototypes.
- **Ask the agent first**, not the author. Any question that recurs gets
  automated (a daily customer-feedback summary runs in the background).
- **Review is split.** The agent does style, linting, bug catching, fixes before
  commit, and tests. People review where it matters: legal risk, trust
  boundaries, security-sensitive code, and product sense and taste.
- **Roles blur.** PMs code; engineers do content and design. Team kept flat.
  Pods decide their own rituals and which workflow to hand to agents first.
- **Kill processes that no longer work.**

## Metrics they watch

1. Onboarding ramp time (people ship real code in week one).
2. PR cycle time. Warning: build systems and CI may not keep up with the volume.
3. Share of agent-assisted commits. No unassisted commit seen in four months.

## Quotes

- "Verification, code review, and security took their place."
- "Our planning ritual shifted away from design docs toward discussions in PRs or prototypes."
- "The new norm is human review where it matters"
- "the right balance of trust vs. verify will keep changing as the models improve."
- "don't confuse throughput with success."
- "pick your noisiest workflow."

## Not in the page

Environments (dev, staging, prod), branching, repo structure, CI/CD design, and
documentation written for agents are not discussed.
