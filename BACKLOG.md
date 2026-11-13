# Backlog

Things asked for and set aside, newest first. Each entry keeps the ask in Trevor's
terms so a later session can pick it up without the conversation it came from.

## 2026-11-13 · Dev and prod for a site that agents post to

**Where the project is heading.** The portfolio is turning into a shared, deployed
page where agents post work. Portfolio work does not have to be done from a
portfolio session: a session in any project repo can write the article, add the
project and publish. That is what makes it agent native.

**The problem.** Seeing the result of a change, including the browser check and
its screenshots on the real host, still needs a deploy. Today every push to
`main` is a deploy to the one live site.

**Options Trevor raised.**

1. Two branches on `teajuw/trevorju.dev`: agents push to `dev`, and `dev` is
   promoted to prod. Open question: "dev and prod", or just "dev and main"?
2. Two domains: `trevorju.dev` is dev and `trevorju.com` (Trevor's second domain)
   is prod.

**What was asked for.**

- Break the options down and say how each would actually be useful.
- Simplify, clarify and strengthen the design of the site as a collaborative
  space that agents post to. What would make it better?
- A tier list, with visuals.

**Status.** Not started. Paused on purpose for the research in
`research/agent-native-orgs/`, which should inform the answer.
