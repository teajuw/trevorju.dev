---
name: publish
description: Publish the portfolio to trevorju.dev. Use only when Trevor says "/publish", "publish", "deploy" or "ship the site".
---

# Publish

A push to `main` is the deploy: `.github/workflows/site.yml` builds the site and puts it on GitHub Pages.

1. Run `/check`. Stop on any error.
2. `git status --short`. If there are uncommitted changes, show them and ask whether they belong in this publish. Commit what does, with a message that says what changed on the site.
3. `git pull --ff-only`, then `git push origin main`.
4. Watch the deploy: `gh run watch $(gh run list --workflow site --limit 1 --json databaseId --jq '.[0].databaseId') --exit-status`.
5. When it finishes, confirm the live site: `curl -sI https://trevorju.dev/ | head -1` and the same for one article and `/llms.txt`.
6. Report the commit that was published and whether the live pages answered. If the run failed, show the failing step's log and do not retry blindly.
