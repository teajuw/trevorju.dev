# Hosting options for a preview per pull request

Written 2026-11-13 for design B in `BACKLOG.md`: a session opens a pull request,
the pull request gets its own address, the browser check runs against that
address, and merging is the publish.

Figures were read from each provider's own pages on 2026-11-13 by a research
subagent. Anything it could not confirm is marked **unverified**. Nothing has
been set up or tested.

## What the site needs

- A preview address for every pull request, at the root of a domain. The site
  uses root-absolute addresses such as `/assets/site.css`, so a preview in a
  subfolder would load production's assets.
- The build as it is: Python, plus the project submodules checked out.
- The workflow has to learn the preview address so `shots.py` can run against it
  and post screenshots on the pull request.
- Previews kept out of search results.
- Production left alone unless there is a reason to move it.

## The options

| | How it works | What it costs on the free plan | How the workflow gets the address | Catch |
|---|---|---|---|---|
| **E. Build in GitHub Actions, upload previews to Cloudflare Pages** | The existing workflow builds `_site/` and uploads it with `wrangler pages deploy --branch=pr-<N>` | 20,000 files, 25 MiB per file | A step output, in the same job | Needs a Cloudflare account and an API token stored as a repo secret |
| **C. Vercel, connected to the repo, previews only** | Vercel builds every branch itself | 100 deployments a day, 1 build at a time | An event Vercel sends to the repo, with the address in it | Whether its builders run `python build.py` is unverified; free-plan terms unverified |
| **B. Netlify, connected to the repo, previews only** | Netlify builds every pull request itself | Previews cost 0 credits | Predictable: `deploy-preview-<N>--<site>.netlify.app`; the job polls it | Never move production there: 15 credits per production deploy out of 300 a month |
| **A. Cloudflare Pages, connected to the repo** | Cloudflare builds every branch itself | 500 builds a month, 1 at a time | Computed from the branch name; the job polls it | Submodule support unverified |
| **D. Stay on GitHub Pages, previews in a subfolder** | A community action commits each preview into `pr-preview/pr-<N>/` on a `gh-pages` branch | Nothing | A step output | GitHub Pages has no native previews. This forces production to deploy from a branch, breaks root-absolute addresses, and puts previews on the production domain with no noindex |

Addresses:

- E: `pr-<N>.<project>.pages.dev`, stable per pull request, noindex added automatically.
- C: `<project>-git-<branch>-<scope>.vercel.app`, stable per branch.
- B: `deploy-preview-<N>--<site>.netlify.app`, noindex added automatically.
- A: `<branch>.<project>.pages.dev`, noindex added automatically.
- D: `https://trevorju.dev/pr-preview/pr-<N>/`.

## Recommendation: E

Production stays on GitHub Pages exactly as it is. The preview is one extra step
in a workflow that already checks out the submodules and runs the Python build,
so none of the "does their builder support this" questions come up. The address
comes back as a step output, the preview sits at a domain root, and it is kept
out of search by default.

What it takes:

1. A Cloudflare account and an empty Pages project (Direct Upload).
2. An API token limited to Cloudflare Pages: Edit, saved with the account id as
   two repo secrets.
3. A second workflow that runs on pull requests: build, upload, run `shots.py`
   against the address, post the screenshots as a comment.
4. `/portfolio:publish` opens a pull request instead of pushing to `main`.

## Risks of E

- **The token is readable by workflows on agent-written branches.** Pull
  requests come from branches in the same repo, so a workflow change in a pull
  request can use the secret. Scoping the token to Pages only limits the damage
  to preview deployments.
- **Cloudflare now points new projects at Workers** instead of Pages. Pages is
  not deprecated, but it may stop improving.
- **A Direct Upload project cannot later be switched** to Cloudflare's own
  build-from-git mode. Moving production there later would mean a new project.
- **Unverified:** whether uploads count against the 500 builds a month.

## The second domain

`trevorju.com` is not needed for any of this. Its best use is as a plain
redirect to `trevorju.dev`. A custom domain for previews is possible on
Cloudflare one branch at a time, which does not fit a preview per pull request.

## Not decided

- Which changes may merge without approval. The suggestion: a sync that only
  moves a pin and its notes merges once checks pass; a new article, or a change
  to templates or `build.py`, waits for Trevor.
- Whether a push to a project repo should open the sync pull request by itself.
