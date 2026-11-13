# bar2vec

## What it is
A music-structure project: it cuts a song into sections and names each one (intro, verse, chorus, bridge and so on) from frozen audio embeddings, one vector per bar. Both parts were tuned as hill climbs against the Harmonix Set with a random train / held-out split and a locked 180-song final test. Final test: cutter 72.7 (boundary F within 3 s) and 53.9 (within 0.5 s) with no training; namer macro-F1 55.9 with rules and 65.9 with a trained classifier. It began as a moment-search prototype on one playlist, and those pages are still in the repo.

## Where things are
- `article/` — the article for the site and its two climb charts.
- `PROCESS.md` — the full process log: timeline, every round, who decided what, what can and cannot be claimed, how to reproduce the final rows. Start here.
- `cuts.json`, `scripts/cuts.py` — the cutter and its settings (the surface the first climb tuned). `scripts/hx_run.py` scores it.
- `names.json`, `scripts/names.py` — the namer and its settings (the second climb). `scripts/nm_run.py` scores it; `scripts/name_model.py` is the trained classifier.
- `scripts/` — everything else: `hx_*` prepare and embed Harmonix songs (download, align, bar tracking, embeddings), `playlist_bars.py` and `breakdown_bars.py` run the cutter and namer on the playlist, `make_*_page.py` build the HTML pages, `bar_transformer.py` is the dropped bar-level transformer.
- `.claude/hillclimb/` — one folder per climb with per-round scores, run logs, `narrative.md` and `_state.json` (split ids). `song-cuts` and `section-names` are the two climbs; `*-final` are the locked test runs.
- `data/` — track lists, alignment results, bar positions, small fitted models and page data. Embeddings (`*.npz`), audio and model weights are not in the repo.
- `breakdown.html`, `similar.html`, `readout.html`, `results_*.html` — generated pages for the playlist. `breakdown.html` shows three cutters per song with names and a scrubbing playhead; it needs the local audio to play.
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
- The learned keep-or-drop filter on cuts (75.4) is kept only as a separate supervised row; the training-free cutter is the project's cutter, because the filter was learned from one pop-heavy dataset.
- Git history before 2026-11-13 was squashed when the repo went public, to remove paper PDFs and a download record.

## Parked
- Scoring names on bar2vec's own cuts (so far only on annotated boundaries).
- Using block-to-block similarity in naming, so neighbours that sound different do not get the same name; learned attention is parked behind it.
- Re-cutting inside a long section at a finer scale.
- Section-by-section song similarity.
- Testing on music outside Harmonix.
- Tempo doubling or halving on about 15 of 81 playlist songs.
- Separating the encoder gain in cutter round 10 from dropping the repeat-to-10-s step.
