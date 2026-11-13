# How an article should read

An article is a project's `README.md`. These are Trevor's preferences for how
one opens and what it shows. Any agent drafting or reviewing a project README
for this site reads this file first.

## The three rules

1. **Start with one standalone sentence.** Directly under the title, alone in
   its own paragraph: what the project is and why it matters. It has to make
   sense with nothing else around it, because it is also the one-liner on the
   home page and the first line an LLM is handed.

   > Double-click a Markdown file. Read it in Claude Desktop. No tokens.

2. **Surface the key numbers early.** The few numbers that prove the project
   worked come before the first section heading, not buried in a results
   section. Each number says what it measures and against what.

   > Pass rate went from 61% to 84% on 120 held-out cases, at a third of the cost per run.

3. **Use visuals.** At least one, and the first one early: a diagram of how it
   works, a screenshot or short clip of it running, or a chart of the result.
   A visual that only decorates does not count. Every image has alt text that
   says what it shows, since the markdown twin and an LLM reader get the alt
   text and not the picture.

## What `/check` looks for

| Rule | Check | On failure |
|---|---|---|
| One standalone sentence | The first paragraph after the title is a single short paragraph, not a list, badge row or heading. | warn |
| Numbers early | At least one figure appears before the first `##` heading. | warn |
| Visuals | At least one image or diagram in the README, with alt text. | warn |

These warn and never block. A project with no result to measure yet has no
number to show, and inventing one is worse than leaving it out.

## Not decided yet

Anything beyond the three rules above: length, section order, tone, how code
is shown. Add rules here as they come up, in Trevor's words.
