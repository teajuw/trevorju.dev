#!/usr/bin/env python3
"""Open the built site in a real browser, try the things a person would, and save screenshots.

    python shots.py                      check _site/ (run build.py first)
    python shots.py https://trevorju.dev check the live site
    python shots.py --out some/folder    where the screenshots go (default: a temp folder)

build.py --check can only read files. This drives a browser, so it catches what a
file check cannot: a link that does nothing, a panel that stays open, a page that
is missing its stylesheet. Prints one line per check and exits 1 if any failed.
The session that made a change should look at every screenshot it prints.

Needs Playwright:  pip install playwright && python -m playwright install chromium
"""
import functools
import http.server
import sys
import tempfile
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent
DESKTOP = {"width": 1440, "height": 900}
PHONE = {"width": 390, "height": 844}

results = []


def check(name, ok, detail=""):
    results.append(ok)
    print(("pass " if ok else "FAIL ") + name + (f"  ({detail})" if detail and not ok else ""))


def serve(folder):
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    handler = functools.partial(Quiet, directory=str(folder))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{server.server_address[1]}"


def styled(page):
    """True when the stylesheet has applied: the header is a flex row and the title is large."""
    return page.evaluate(
        "() => getComputedStyle(document.querySelector('.nav .wrap')).display === 'flex'"
        " && parseFloat(getComputedStyle(document.querySelector('h1')).fontSize) > 30")


def panel_shown(page):
    return page.evaluate("() => getComputedStyle(document.querySelector('#spyPanel')).visibility === 'visible'")


def main():
    args = sys.argv[1:]
    out = Path(tempfile.mkdtemp(prefix="site-shots-"))
    if "--out" in args:
        i = args.index("--out")
        out = Path(args[i + 1])
        del args[i:i + 2]
        out.mkdir(parents=True, exist_ok=True)
    base = args[0].rstrip("/") if args else serve(ROOT / "_site")

    def shot(page, name):
        path = out / f"{name}.png"
        page.screenshot(path=str(path))
        print(f"shot  {path}")

    with sync_playwright() as p:
        browser = p.chromium.launch()

        # ---- home ----
        ctx = browser.new_context(viewport=DESKTOP)
        page = ctx.new_page()
        page.goto(base + "/", wait_until="networkidle")
        check("home: stylesheet applied", styled(page))
        check("home: assets are stamped with a version",
              page.evaluate("() => [...document.querySelectorAll('link[rel=stylesheet][href^=\"/assets\"],script[src^=\"/assets\"]')]"
                            ".every(e => (e.href || e.src).includes('?v='))"))
        check("home: no section indicator", page.evaluate("() => document.querySelector('#spy').hidden"))
        check("home: no sideways scroll", page.evaluate("() => document.documentElement.scrollWidth <= innerWidth"))
        shot(page, "home-desktop")
        first = page.get_attribute("a.row", "href")
        check("home: has a project to open", bool(first))
        article = base + (first or "/")

        # ---- article, desktop ----
        page.goto(article, wait_until="networkidle")
        check("article: stylesheet applied", styled(page))
        check("article: no sideways scroll", page.evaluate("() => document.documentElement.scrollWidth <= innerWidth"))
        shot(page, "article-desktop")
        gaps = page.evaluate(
            "() => { const t = document.querySelector('.prose').getBoundingClientRect(),"
            " w = document.querySelector('.wrap'), s = getComputedStyle(w), r = w.getBoundingClientRect();"
            " return [t.left - r.left - parseFloat(s.paddingLeft), r.right - parseFloat(s.paddingRight) - t.right]; }")
        check("article: the text column is centred on the page", abs(gaps[0] - gaps[1]) <= 2,
              f"left {gaps[0]:.0f}px, right {gaps[1]:.0f}px")

        sections = page.locator("#spyPanel a").count()
        check("article: indicator lists the sections", sections > 1, f"{sections} found")
        if sections > 1:
            page.hover("#spyTicks")
            page.wait_for_timeout(300)
            check("indicator: opens on hover", panel_shown(page))
            shot(page, "article-indicator-open")
            # Click the last section and leave the pointer exactly where it is.
            page.locator("#spyPanel a").last.click()
            page.wait_for_timeout(60)
            check("indicator: closes the moment a section is chosen", not panel_shown(page))
            page.wait_for_timeout(900)
            check("indicator: stays closed while the pointer rests there", not panel_shown(page))
            check("indicator: the page jumped", page.evaluate("() => scrollY > 100"), "scrollY did not move")
            shot(page, "article-after-jump")
            page.mouse.move(700, 500)
            page.wait_for_timeout(100)
            page.hover("#spyTicks")
            page.wait_for_timeout(300)
            check("indicator: opens again after the pointer leaves and returns", panel_shown(page))
            page.mouse.move(700, 500)

        ctx.grant_permissions(["clipboard-read", "clipboard-write"])
        page.goto(article, wait_until="networkidle")
        if page.locator("#copyLLM").count():
            page.click("#copyLLM")
            page.wait_for_timeout(300)
            copied = page.evaluate("() => navigator.clipboard.readText()")
            check("copy for LLM: puts the page's markdown on the clipboard", copied.startswith("<!-- source:"), copied[:40])
        ctx.close()

        # ---- phone ----
        ctx = browser.new_context(viewport=PHONE, device_scale_factor=2, is_mobile=True, has_touch=True)
        page = ctx.new_page()
        for name, url in (("home-phone", base + "/"), ("article-phone", article)):
            page.goto(url, wait_until="networkidle")
            check(f"{name}: stylesheet applied", styled(page))
            check(f"{name}: no sideways scroll", page.evaluate("() => document.documentElement.scrollWidth <= innerWidth"))
            check(f"{name}: the opening paragraph uses the full width",
                  page.evaluate("() => document.querySelector('.head .lede').getBoundingClientRect().width > innerWidth * 0.8"))
            shot(page, name)
        ctx.close()
        browser.close()

    failed = results.count(False)
    print(f"{len(results)} checks, {failed} failed. Screenshots in {out}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
