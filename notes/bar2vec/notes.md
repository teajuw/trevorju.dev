# bar2vec

## What it is
A music-structure project: it cuts a song into sections and names each one (intro, verse, chorus, bridge and so on) from frozen audio embeddings, one vector per bar. Both parts were tuned as hill climbs against the Harmonix Set with a random train / held-out split and a locked 180-song final test. Final test: cutter 72.7 (boundary F within 3 s) and 53.9 (within 0.5 s) with no training; namer macro-F1 55.9 with rules and 65.9 with a trained classifier. It began as a moment-search prototype on one playlist, and those pages are still in the repo.

## Where things are
- `article/` — the article for the site (it opens with a Terms section; use those words: bar, embedding, audio model, similarity grid, cut, cutter, namer, rules, classifier; it ends with a Sources section, cited in the text as `[n]`, following the site's ARTICLES.md) and its climb charts (step graphs: kept rounds as a staircase, hollow dots for rounds not kept); the article shows only `climb.svg`, `names.svg` is unused. The article is kept short, about 1,250 words: round-by-round detail lives in `PROCESS.md`, which it links to.
- `article/demo/` — the live demo shown at the top of the page, two stacked parts with no tabs, "Listen to the result" then "See how it works": `index.html` embeds six songs' official YouTube uploads and draws bar2vec's sections under the player; `sections.json` is its data, made by `scripts/demo_songs.py` from `songs.json`. A search box covers 265 more songs in `catalogue.json`: the top 40 of each Billboard year-end Hot 100, 2018 to 2025, that have an upload on the artist's own channel allowing embedding (`scripts/catalogue_list.py` builds the list into `data/catalogue_candidates.json`, `scripts/catalogue_match.py` finds the uploads into `data/catalogue_songs.json`, `scripts/demo_songs.py --catalogue` runs the pipeline and deletes each song's audio). The second part is an animation, started the first time it scrolls into view, following one bar of one song through the method, including inside the audio model (patches, each patch's 768 numbers, the twelve layers, joining and averaging into 3,840): `onebar.js` draws it from `bar.json`, made by `scripts/bar_story_data.py`. No audio is hosted; the audio fetched for analysis stays in the git-ignored `audio_demo/`.
- `PROCESS.md` — the full process log: timeline, every round, who decided what, what can and cannot be claimed, how to reproduce the final rows. Start here.
- `cuts.json`, `scripts/cuts.py` — the cutter and its settings (the surface the first climb tuned). `scripts/hx_run.py` scores it.
- `names.json`, `scripts/names.py` — the namer and its settings (the second climb). `scripts/nm_run.py` scores it on annotated boundaries; `scripts/nm_e2e.py` scores names end to end on the cutter's own cuts, by time; `scripts/name_model.py` is the trained classifier. `scripts/nm_cuts_fit.py` fits and scores namers end to end on the cutter's own cuts (third climb, record in `.claude/hillclimb/section-names-cuts/`); its "stack" regime, the section classifier with per-bar votes added to its inputs, is saved as `data/name_model_cuts.joblib` and is what `scripts/demo_songs.py` uses. Per-bar embeddings of the catalogue songs are kept in the git-ignored `data/catalogue_cache/`, so re-naming needs no audio.
- `scripts/` — everything else: `hx_*` prepare and embed Harmonix songs (download, align, bar tracking, embeddings), `playlist_bars.py`, `playlist_bars_extra.py` and `breakdown_bars.py` run the cutter and the trained namer on the playlist (`--namer rules` for the rule names), `make_*_page.py` build the HTML pages, `bar_transformer.py` is the dropped bar-level transformer.
- `.claude/hillclimb/` — one folder per climb with per-round scores, run logs, `narrative.md` and `_state.json` (split ids). `song-cuts` and `section-names` are the two climbs; `*-final` are the locked test runs; `section-names-e2e` holds the end-to-end name scores.
- `data/` — track lists, alignment results, bar positions, small fitted models and page data. Embeddings (`*.npz`), audio and model weights are not in the repo.
- `breakdown.html`, `similar.html`, `readout.html`, `results_*.html` — generated pages for the playlist. `breakdown.html` shows three cutters per song with names and a scrubbing playhead; names come from the trained classifier, and a name it gives less than 0.8 probability ends in `?`; it needs the local audio to play.
- `papers/` — notes on music language models with links to ten arXiv papers.
- `spotify-landscape-2026-11/` — the research pass on what Spotify and competitors ship, and the idea list the project came from.
- `brief.md`, `brief-song-structure.md` — the project brief and a paper-style brief for the structure work.

## How to run it
- Python with `uv`; scripts run from the repo root as `uv run scripts/<name>.py`.
- Nothing runs from a fresh clone without the audio: Harmonix does not distribute it, so `scripts/hx_download.py` and `scripts/hx_align.py` have to fetch and align it first, and the embedding scripts need the model weights in `models/` and `external/`.
- Score a cutter round: `uv run scripts/hx_run.py --variant <name>`. Score a naming round: `uv run scripts/nm_run.py`. The exact commands for the final rows are at the end of `PROCESS.md`.
- There are no unit tests. The climbs' recorded per-song grades act as the regression check: the runner reproduced all 307 before the final test.

## Tried and dropped
- Fixed 10 s windows as the unit: replaced by one embedding per bar, the largest single gain (+17).
- A window every 2 s, block matching alone, and three bars of context per vector: each reverted, no held-out gain.
- Beat-level cut placement: about 100 rule settings and a learned placer, none beat noise; a control trained on shuffled targets got about half the placer's gain.
- Chroma change score, a guard gap between compared sides, other encoder layers, per-song PCA: no gain on tuning songs, no round spent.
- Naming by matching a section to a text prompt: scores at chance.
- Loudness as a hint for the chorus group: gained on tuning songs, failed on held-out.
- A bar-level transformer for naming: about 45 macro-F1 in cross-validation against 63 for boosted trees on the same 150 songs. Attention helped, rare labels were not learned.
- Doubling the training labels with 213 partly aligned Harmonix songs: +0.3 ±2.4 on held-out, not adopted.
- Using neighbour similarity to rename sections: short lead-in to the chorus becomes prechorus, sounds like the chorus group becomes chorus, neighbour order in the chorus pick. Best +0.5 ±0.6 on the tuning songs, no held-out round spent. The flag itself is reliable (such a verse is truly a verse 47% of the time against 73% otherwise), and was shown on the playlist page as `verse?` until the trained namer replaced the rule names there.
- The static step-by-step figure (`process.svg`), the round-by-round tables and the naming chart in the article: removed when the user asked for a short page; the animation shows the same steps with real data and every round is in `PROCESS.md`.
- Tabs in the demo: replaced by two stacked parts, listening first, at the user's request.
- Horizontal bar charts in the article: replaced by step graphs, which show the shape of a climb and are shorter on screen.
- The learned keep-or-drop filter on cuts (75.4) is kept only as a separate supervised row; the training-free cutter is the project's cutter, because the filter was learned from one pop-heavy dataset.
- For the demo: hosting freely licensed music (the well-known free recordings are not pop form) and 30-second store previews (too short to show structure); embedding official YouTube uploads was used instead.
- Letting visitors look up any song: the YouTube player gives a page no audio, fetching it on request breaks YouTube's terms, and the site has no server. A catalogue processed ahead of time is used instead.
- An unpaced run of the upload matcher: YouTube refused it partway and 88 songs were recorded as missing; requests are now spaced and errored lookups retried.
- Git history before 2026-11-13 was squashed when the repo went public, to remove paper PDFs and a download record.
- Fitting the trained namer on the cutter's own sections: +2.7 ±2.2 on tuning songs, +0.1 ±2.2 on held-out, not kept. The 13-point loss on cuts is about 4 from misplaced edges and 8 from the classifier's inputs changing when edges move.
- Per-bar votes alone, with no section classifier: +2.1 ±2.5 on tuning songs, not scored on held-out; the votes are used as extra inputs instead (held-out 53.1 to 55.8, +2.7 ±2.3, kept by 0.4 over noise).

## Parked
- Scoring the bar-vote namer once on the 180 locked songs, which have never been scored end to end. The playlist page still uses the earlier classifier.
- Listening to the trained names on the playlist page, the six demo songs and the 265 catalogue songs (none has annotations, so nothing there is scored). Across the catalogue 29% of sections are marked unsure and 8 songs have no section named chorus (with the bar-vote namer; 444 of 2,480 demo names changed when it came in and none has been listened to); the catalogue videos were accepted on YouTube's embedding flag and not all played in a browser.
- Learned attention between sections for naming (the rule-based stand-in was tried and dropped); worth returning to with more labelled songs or pretraining on unlabelled music.
- Other ways of grouping bars (k-means, spectral clustering) for the chorus pick, and nearest neighbours across songs for names. Either would reopen the naming climb, which the stopping rule closed.
- Re-cutting inside a long section at a finer scale.
- Section-by-section song similarity.
- Testing on music outside Harmonix.
- Tempo doubling or halving on about 15 of 81 playlist songs.
- Separating the encoder gain in cutter round 10 from dropping the repeat-to-10-s step.
