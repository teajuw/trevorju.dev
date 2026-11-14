#!/usr/bin/env python3
"""Build trevorju.dev: projects/* + notes/* + templates/ -> _site/.

    python build.py            build
    python build.py --check    build, then fail on errors and print warnings

Every project is a git submodule under projects/. Its article/article.md is the
article (README.md if there is none), and its pinned commit gives the "built
from" id and the "last updated" date. ARTICLES.md is the standard.
"""
import hashlib
import html
import posixpath
import re
import shutil
import urllib.parse
import subprocess
import sys
import tomllib
from datetime import datetime
from pathlib import Path

import markdown

ROOT = Path(__file__).parent
OUT = ROOT / "_site"
TPL = ROOT / "templates"


def git(*args, cwd=ROOT):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def fill(template, **values):
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    return template


def take_paragraph(lines):
    """Pop the next paragraph off the front if it is prose; otherwise leave the lines alone."""
    while lines and not lines[0].strip():
        lines.pop(0)
    first = []
    while lines and lines[0].strip():
        first.append(lines.pop(0).strip())
    para = " ".join(first)
    if para[:1] in "#-*`<!|>" or re.match(r"\d+\.", para):
        # Not a sentence (a list, heading, badge row...): leave it in the body.
        lines[:0] = first
        return ""
    return para


def split_article(text, with_abstract):
    """Title, the one sentence, the abstract, and the rest.

    A README used as a fallback has no abstract: its second paragraph is body text.
    """
    lines = text.strip().splitlines()
    title = ""
    if lines and lines[0].startswith("# "):
        title = lines.pop(0)[2:].strip()
    lede = take_paragraph(lines)
    abstract = take_paragraph(lines) if with_abstract and lede else ""
    return title, lede, abstract, "\n".join(lines).strip()


def render(md_text):
    return markdown.markdown(md_text, extensions=["fenced_code", "tables", "sane_lists"])


def inline(md_text):
    return re.sub(r"^<p>|</p>$", "", render(md_text).strip())


ABSOLUTE = re.compile(r"([a-z][a-z0-9+.-]*:|#|/)", re.I)


def repo_url(p, url, raw):
    """A link relative to the article file, as a URL into the repo at the pinned commit."""
    path = posixpath.normpath(posixpath.join(p["base"], url))
    host = f"https://raw.githubusercontent.com/{p['repo']}/{p['sha']}/" if raw else f"https://github.com/{p['repo']}/blob/{p['sha']}/"
    return host + path


def absolutize(page_html, p):
    """Relative images are copied next to the page; relative links point into the repo."""
    def fix(match):
        attr, url = match.group(1), match.group(2)
        if ABSOLUTE.match(url):
            return match.group(0)
        if attr == "src":
            image = (p["folder"] / p["base"] / url).resolve()
            if image.is_file() and p["folder"].resolve() in image.parents:
                target = OUT / p["slug"] / "assets" / image.name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(image, target)
                return f'src="/{p["slug"]}/assets/{image.name}"'
        return f'{attr}="{repo_url(p, url, attr == "src")}"'
    page_html = re.sub(r'(src|href)="([^"]+)"', fix, page_html)
    # An image whose file is a video becomes a silent looping player, with the alt text as its label.
    return re.sub(r'<img alt="([^"]*)" src="([^"]+\.(?:mp4|webm))"\s*/?>',
                  r'<video src="\2" aria-label="\1" autoplay muted loop playsinline controls></video>', page_html)


def absolutize_md(text, p):
    """The same for the markdown twin, so an LLM reader can follow every link."""
    def fix(match):
        bang, label, url = match.group(1), match.group(2), match.group(3)
        return match.group(0) if ABSOLUTE.match(url) else f"{bang}[{label}]({repo_url(p, url, bool(bang))})"
    return re.sub(r"(!?)\[([^\]]*)\]\(([^)\s]+)\)", fix, text)


def youtube(page_html):
    """A paragraph that is only a YouTube link becomes a player, keeping the link's start (t or start) and end times."""
    def embed(match):
        url = urllib.parse.urlparse(html.unescape(match.group(1)))
        q = urllib.parse.parse_qs(url.query)
        vid = url.path.strip("/") if url.netloc.endswith("youtu.be") else q.get("v", [""])[0]
        if not re.fullmatch(r"[\w-]{6,20}", vid):
            return match.group(0)
        secs = lambda k: re.sub(r"\D", "", q.get(k, [""])[0])  # noqa: E731
        args = [f"{name}={v}" for name, v in (("start", secs("t") or secs("start")), ("end", secs("end"))) if v]
        src = f"https://www.youtube-nocookie.com/embed/{vid}" + ("?" + "&amp;".join(args) if args else "")
        return (f'<iframe class="yt" src="{src}" title="YouTube video" loading="lazy" '
                'allow="accelerometer; encrypted-media; gyroscope; picture-in-picture; fullscreen" allowfullscreen></iframe>')
    return re.sub(r'<p><a href="(https://(?:(?:www\.)?youtube\.com/watch\?|youtu\.be/)[^"]+)">[^<]*</a></p>', embed, page_html)


def demo_frame(p):
    """The project's demo page in a frame. site.js sets the height the demo reports; 560px holds until it does."""
    if not p["demo"]:
        return ""
    return (f'<iframe class="demo" src="/{p["slug"]}/demo/" title="{html.escape(p["title"])} live demo" loading="lazy" '
            'allow="autoplay; encrypted-media; fullscreen; picture-in-picture" style="height:560px"></iframe>\n')


def demote(notes_text):
    """notes.md, moved one heading level down so it sits under the article."""
    out = []
    for line in notes_text.strip().splitlines():
        if line.startswith("# "):
            line = "## Notes"
        elif line.startswith("#"):
            line = "#" + line
        out.append(line)
    return "\n".join(out)


def read_project(site, folder, slug, url, is_self=False):
    repo = url.split("github.com/")[-1]
    full_sha = git("rev-parse", "HEAD", cwd=folder)
    date = datetime.strptime(git("log", "-1", "--format=%cs", cwd=folder), "%Y-%m-%d")
    # The article is article/article.md; a project without one falls back to its README.
    # This repo's own entry has no fallback: its README is the documentation, not an article.
    candidates = ("article/article.md",) if is_self else ("article/article.md", "README.md")
    source = next((f for f in candidates if (folder / f).exists()), "")
    text = (folder / source).read_text() if source else ""
    title, lede, abstract, body = split_article(text, with_abstract=source == "article/article.md")
    notes_dir = ROOT / "notes" / slug
    notes = (notes_dir / "notes.md").read_text() if (notes_dir / "notes.md").exists() else ""
    log = (notes_dir / "log.md").read_text() if (notes_dir / "log.md").exists() else ""
    return {
        "slug": slug, "repo": repo, "url": url, "sha": full_sha[:7], "date": date, "self": is_self,
        "folder": folder, "file": source, "base": posixpath.dirname(source),
        "readme": text, "title": title or slug, "has_title": bool(title), "lede": lede, "abstract": abstract, "body": body,
        "notes": notes, "log": log,
        # A live demo is article/demo/index.html: a page of its own, shown in a frame at the top of the article.
        "demo": source == "article/article.md" and (folder / "article" / "demo" / "index.html").is_file(),
        "source_url": f"{url}/tree/{full_sha}",
        "page_url": f"{site['url']}/{slug}/",
        "md_abs": f"{site['url']}/{slug}.md",
    }


def load_projects(site):
    """Live projects: the submodules under projects/, plus this repo if it has an article.

    Submodules under archive/ are kept with their pins, notes and logs but not built.
    """
    projects = []
    listing = git("config", "-f", ".gitmodules", "--get-regexp", r"^submodule\..*\.path$") if (ROOT / ".gitmodules").exists() else ""
    for line in listing.splitlines():
        key, path = line.split(" ", 1)
        if not path.startswith("projects/"):
            continue
        name = key[len("submodule."):-len(".path")]
        url = git("config", "-f", ".gitmodules", f"submodule.{name}.url").removesuffix(".git")
        projects.append(read_project(site, ROOT / path, Path(path).name, url))
    if (ROOT / "article" / "article.md").exists():
        projects.append(read_project(site, ROOT, site.get("self_slug", "portfolio"), site["repo"], is_self=True))
    projects.sort(key=lambda p: p["date"], reverse=True)
    return projects


def twin(p):
    """The page as markdown: what Copy for LLM copies and what agents fetch."""
    head = f"<!-- source: {p['source_url']} | last updated: {p['date']:%Y-%m-%d} | page: {p['page_url']} -->"
    parts = [head, absolutize_md(p["readme"].strip(), p)]
    if p["demo"]:
        parts.append(f"Live demo: {p['page_url']}demo/")
    if p["notes"]:
        parts += ["---", demote(p["notes"])]
    return "\n\n".join(parts) + "\n"


def build():
    site = tomllib.loads((ROOT / "site.toml").read_text())
    projects = load_projects(site)
    esc = html.escape

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)
    for name in ("tokens.css", "site.css", "site.js"):
        shutil.copy(TPL / name, OUT / "assets" / name)
    for name in ("CNAME", ".nojekyll"):
        if (ROOT / name).exists():
            shutil.copy(ROOT / name, OUT / name)

    # Browsers keep the stylesheet and script for ten minutes. A new page with an old
    # stylesheet looks broken, so each build stamps their addresses with a hash of their contents.
    stamp = hashlib.sha1(b"".join((TPL / n).read_bytes() for n in ("tokens.css", "site.css", "site.js"))).hexdigest()[:8]
    base = (TPL / "base.html").read_text().replace("{{v}}", stamp)
    host = site["url"].split("//")[-1]
    first, _, rest = host.partition(".")
    brand = f"{esc(first)}<i>.</i>{esc(rest)}" if rest else esc(host)

    # home
    rows = []
    for p in projects:
        rows.append(
            f'    <a class="row grid" href="/{p["slug"]}/">'
            f'<span class="side mono when">{p["date"]:%b %d, %Y}</span>'
            f'<span class="what"><span class="t">{esc(p["title"])}</span><span class="d">{inline(p["lede"])}</span></span>'
            f'<span class="arr">→</span></a>'
        )
    for _ in range(site.get("blanks", 0)):
        rows.append(
            '    <div class="row grid blank"><span class="side mono when">—</span>'
            f'<span class="what"><span class="t">{esc(site.get("blank_title", "Next project"))}</span>'
            f'<span class="d">{esc(site.get("blank_text", "Write-up in progress."))}</span></span></div>'
        )
    def abstract_html(text):
        return " " + inline(text) if text else ""

    home = fill(
        (TPL / "home.html").read_text(), name=esc(site["name"]), tagline=esc(site["tagline"]),
        abstract=abstract_html(site.get("abstract", "")),
        facts="\n".join(
            f'      <div><dt>{label}</dt><dd><a href="{esc(site[key])}">{esc(site[key].rstrip("/").split("/")[-1])}</a></dd></div>'
            for label, key in (("GitHub", "github"), ("LinkedIn", "linkedin")) if site.get(key)),
        rows="\n".join(rows))
    (OUT / "index.html").write_text(fill(
        base, title=esc(site["name"]), description=esc(site["tagline"]), md_url="/llms.txt", brand=brand, body=home))

    # articles and their markdown twins
    article = (TPL / "article.html").read_text()
    for p in projects:
        page = fill(
            article,
            title=esc(p["title"]), standfirst=inline(p["lede"]), abstract=abstract_html(p["abstract"]),
            repo=esc(p["repo"]), repo_url=esc(p["url"]),
            updated=f"{p['date']:%b %d, %Y}", sha=p["sha"],
            source_url=esc(p["source_url"]), slug=p["slug"],
            page_url=esc(p["page_url"]), md_abs=esc(p["md_abs"]),
            content=demo_frame(p) + youtube(absolutize(render(p["body"]), p)),
        )
        (OUT / p["slug"]).mkdir(exist_ok=True)
        if p["demo"]:
            shutil.copytree(p["folder"] / "article" / "demo", OUT / p["slug"] / "demo", symlinks=False)
        (OUT / p["slug"] / "index.html").write_text(fill(
            base, title=f"{esc(p['title'])} · {esc(site['name'])}", description=esc(p["lede"]),
            md_url=f"/{p['slug']}.md", brand=brand, body=page))
        (OUT / f"{p['slug']}.md").write_text(twin(p))

    # llms.txt and llms-full.txt
    summary = " ".join(filter(None, [site["tagline"], site.get("abstract", "")]))
    index = [f"# {site['name']}", "", f"> {summary}", "",
             "Each project page is built from its own GitHub repo at a pinned commit. "
             "Every page has a markdown twin at the same URL with `.md`.", "", "## Projects", ""]
    index += [f"- [{p['title']}]({p['md_abs']}): {p['lede']}" for p in projects]
    index += ["", "## Source", "", f"- [This site's repo]({site['repo']}): `git clone --recursive {site['repo']}` gets every project at its pinned commit",
              f"- [Everything in one file]({site['url']}/llms-full.txt)", ""]
    (OUT / "llms.txt").write_text("\n".join(index))
    full = [f"# {site['name']}", "", f"> {summary}", ""] + [twin(p) for p in projects]
    (OUT / "llms-full.txt").write_text("\n".join(full))
    return site, projects


def check_sources(text):
    """The Sources rules in ARTICLES.md: [n] in the text and the numbered list under ## Sources agree."""
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    heads = re.findall(r"^## +(.+?)\s*$", text, flags=re.M)
    body, _, sources = text.partition("\n## Sources")
    cited = {int(n) for n in re.findall(r"\[(\d+)\](?!\()", re.sub(r"`[^`\n]*`", "", body))}
    entries = {int(n): line for n, line in re.findall(r"^(\d+)\. (.*)$", sources, flags=re.M)}
    if not cited and "Sources" not in heads:
        return []
    out = []
    if "Sources" not in heads:
        return [f"cites {sorted(cited)} but has no ## Sources section"]
    if heads[-1] != "Sources":
        out.append("## Sources is not the last section")
    out += [f"[{n}] is cited but is not in Sources" for n in sorted(cited - set(entries))]
    out += [f"source {n} is never cited in the text" for n in sorted(set(entries) - cited)]
    out += [f"source {n} has no link" for n, line in sorted(entries.items()) if "](http" not in line]
    return out


def check(projects):
    errors, warnings = [], []
    for p in projects:
        s = p["slug"]
        if not p["readme"]:
            errors.append(f"{s}: no article/article.md and no README.md")
            continue
        if p["file"] != "article/article.md" and not p["self"]:
            warnings.append(f"{s}: no article/article.md, so the page is built from README.md")
        if not p["has_title"]:
            errors.append(f"{s}: {p['file']} has no title (a first line starting with '# ')")
        if not (OUT / f"{s}.md").exists():
            errors.append(f"{s}: no markdown twin was built")
        if not p["self"] and not p["notes"]:
            errors.append(f"{s}: notes/{s}/notes.md is missing")
        newest = next((l for l in p["log"].splitlines() if l.strip() and not l.startswith("#")), "")
        if not p["self"] and p["sha"] not in newest:
            errors.append(f"{s}: pinned at {p['sha']} but the newest line of notes/{s}/log.md does not name it; run /sync")
        # ARTICLES.md rules: warn, never block.
        if not p["lede"]:
            warnings.append(f"{s}: {p['file']} does not open with one standalone sentence")
        elif p["file"] == "article/article.md" and not p["abstract"]:
            warnings.append(f"{s}: {p['file']} has no abstract after its opening sentence")
        # Whether an article needs a visual or a number is a judgement, so neither is checked.
        if p["demo"] and any(f.is_symlink() for f in (p["folder"] / "article" / "demo").rglob("*")):
            errors.append(f"{s}: article/demo/ contains a symlink")
        if re.search(r"!\[\s*\]\(", p["readme"]):
            warnings.append(f"{s}: an image has no alt text")
        warnings += [f"{s}: {w}" for w in check_sources(p["readme"])]
    for page in OUT.rglob("*.html"):
        for url in re.findall(r'(?:href|src)="(/[^"#?]*)', page.read_text()):
            target = OUT / url.lstrip("/")
            if not (target.is_file() or (target / "index.html").is_file()):
                errors.append(f"{page.relative_to(OUT)}: broken link {url}")
    for w in warnings:
        print("warn ", w)
    for e in errors:
        print("ERROR", e)
    print(f"{len(projects)} project(s), {len(errors)} error(s), {len(warnings)} warning(s)")
    return not errors


if __name__ == "__main__":
    _, built = build()
    print(f"built {OUT.relative_to(ROOT)}/ with {len(built)} project(s)")
    if "--check" in sys.argv and not check(built):
        sys.exit(1)
