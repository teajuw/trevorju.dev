---
name: check
description: Build the portfolio, validate it, and look at screenshots of the result. Use when Trevor says "/check", after any change to templates, tokens.css, build.py, notes or pins, and before every publish.
---

# Check the site

1. Build and validate: `.venv/bin/python build.py --check`. If `.venv` is missing: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`.
   - An `ERROR` line fails the check: a missing README or title, a missing markdown twin, missing notes, a pin with no log line, a broken link. Fix it or report it; do not publish.
   - A `warn` line is an `ARTICLES.md` rule the README does not meet. Report it; it does not block.
2. Serve the result: `python3 -m http.server 8765 --bind 127.0.0.1 --directory _site` in the background.
3. Take screenshots with headless Chrome into your scratch directory, never into this repo:
   `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --window-size=<w>,<h> --virtual-time-budget=4000 --screenshot=<file> <url>`
   - home at `1440,1000` and `500,900`
   - one article at `1440,1300` and `500,900`
   (Chrome will not go narrower than 500 wide. A screenshot taken after scrolling comes out blank in headless mode; shoot from the top.)
4. Look at every screenshot. Check that nothing overlaps or overflows, the section indicator sits at the top left, and the page you changed looks the way the change intended.
5. Stop the server.
6. Report: errors, warnings, and what you saw in the screenshots. Say plainly if anything was not checked.
