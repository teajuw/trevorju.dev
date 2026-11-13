# 3rd-shot

## What it is
A research pipeline that turns single-camera broadcast video of a pickleball match into a 3D scene: the court, four bodies, their paddles and the ball, in feet and seconds. It runs offline on an Apple Silicon Mac. The longer aim is a simulator that learned players can play in. It was built on one match (the PPA Brisbane 2026 men's doubles final). No licence file for its own code yet.

## Where things are
- `article/` — the article this site builds, its two demo videos, the pipeline diagram and the shot-map figure. It links to the original broadcast at 287 s, which the site shows as a YouTube player. `article/demo/` is the live demo the site frames at the top of the page: the interactive 3D viewer for the same ten seconds (about 5 MB of mesh data).
- `calib/`, `cuts/` — camera calibration from the court lines, and the split of the broadcast into camera shots.
- `players/` — the four players' positions on the court from a keypoint detector.
- `ball/` — 2D ball tracking.
- `fit3d/` — splits a rally into flights, decodes hits and bounces (`decode_events.py`), and fits each flight as a physical 3D trajectory.
- `bodies/` — runs SAM 3D Body and GVHMR, grounds and smooths the meshes, infers the paddle (`paddle.py`), and exports the web viewer's data. `export_demo.py` cuts a time window out of that export for the article's live demo. `render_demo.py` draws the scene straight to video, with no browser and no broadcast footage. `patches/sam-3d-body.patch` makes Meta's code run on Apple GPUs.
- `paddle_seg/` — the attempt to outline paddles with SAM 2.
- `sim/` — ball flight, bounce and paddle-impact model, fitted against tracked flights.
- `shots/` — the table of every detected shot, the models that predict where a shot goes, court geometry, and the hand-check sample.
- `batch/` — whole-match runs of the front stages.
- `eval/` — hand labels for hits and bounces, the scorer, and the labelling page.
- `research_notes/`, `reports/`, `ideas/` — literature reviews and notes behind the design choices.
- `open-items.md`, `optimize.md` — what is parked, and where processing time goes.
- Every stage folder has a `RESULTS.md` with what was measured.

## How to run it
- Set up: `uv sync`. The body models use a second environment at `bodies/.venv`.
- Nothing runs from a fresh clone. The match video, model weights (SAM 3D Body, SMPL, SMPL-X) and the vendored repos are not in the repository; the README says where each goes.
- Shot model, once the front stages have run: `uv run python batch/run_front.py 4`, `uv run python shots/build.py`, `uv run python shots/model.py 7`.
- Article figure: `uv run python shots/figure.py`.
- Article videos: `uv run --with pyvista python bodies/render_demo.py bodies/out/rally_267_grounded bodies/out/rally_267_paddle <out.mp4> 20 30 --view court` (or `broadcast`, `orbit`, `side`, `top`).
- Live demo data: `uv run python bodies/export_demo.py bodies/out/view article/demo 20 30`.
- There are no tests. Each stage is checked by its own numbers in `RESULTS.md`.

## Tried and dropped
From the repo's write-ups and the sessions that built it:
- Picking the paddle's outline automatically by size and shape. SAM 2 outlines a paddle when given a click on it, but the automatic pick chose shorts, banners and the court.
- The first paddle pose, which flipped and passed through bodies. Replaced by one tied to the palm and forearm and rolled at each hit.
- Refitting drag and adding spin to the ball simulator. Neither moved its landing error by more than the noise in 13 test flights.
- Describing a shot's target by direction and share of the available court instead of court feet. It scored 0.17 to 0.20 worse per shot, and mixing the two was no better.
- Contact height and bounce-or-volley as inputs to the shot model. No measurable gain over hitter position.
- A screenshot of the 3D viewer as the article's lead image. Not taken; the lead is now a rendered video.
- Orbit, side and top-down demo videos. Rendered but not used; two views of the same ten seconds were enough.
- The broadcast clip beside the render as a file. Left out, because it would put the tour's footage on a public page; the article embeds the tour's own YouTube upload instead.
- An architecture diagram with parallel tracks and a "camera sees, physics adds" diagram. Drafted; Trevor chose the simple six-step one.
- The repo was first published as a card on the retired `teajuw/portfolio` site by mistake (2026-11-13).

## Parked
- Checking the shot table by hand. A page with 40 random and 20 hard clips exists; Trevor parked it on 2026-11-13 because the automatic labels are poor.
- The hit and bounce detector scores 0.95 on the clips it was tuned on and 0.50 on the one held-out clip. Hand labels for more clips are not done.
- Measuring paddles from pixels: needs SAM 3 access or another source of a click on the paddle (`open-items.md`).
- The newer event decoder is not yet wired into the 3D ball fit.
- One clip (`b_2414`) failed in the whole-match run and was not investigated.
- The simulator's landing-prediction gate is not passed, so the later stages (learned players) have not started.
