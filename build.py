#!/usr/bin/env python3
"""Build trevorju.dev: projects/* + notes/* + templates/ -> _site/.

    python build.py            build
    python build.py --check    build, then fail on errors and print warnings

Every project is a git submodule under projects/. Its README.md is the article,
its pinned commit gives the "built from" id and the "last updated" date.
"""
import html
import re
import shutil
import subprocess
import sys
import tomllib
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import markdown

ROOT = Path(__file__).parent
OUT = ROOT / "_site"
TPL = ROOT / "templates"
WORDS_PER_MINUTE = 230


def git(*args, cwd=ROOT):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def fill(template, **values):
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    return template


def split_readme(text):
    """Title, standalone first paragraph, and the rest."""
    lines = text.strip().splitlines()
    title = ""
    if lines and lines[0].startswith("# "):
        title = lines.pop(0)[2:].strip()
    while lines and not lines[0].strip():
        lines.pop(0)
    first = []
    while lines and lines[0].strip():
        first.append(lines.pop(0).strip())
    lede = " ".join(first)
    if lede[:1] in "#-*`<!|>" or re.match(r"\d+\.", lede):
        # Not a sentence (a list, heading, badge row...): leave it in the body.
        lines = first + lines
        lede = ""
    return title, lede, "\n".join(lines).strip()


def render(md_text):
    return markdown.markdown(md_text, extensions=["fenced_code", "tables", "sane_lists"])


def inline(md_text):
    return re.sub(r"^<p>|</p>$", "", render(md_text).strip())


def absolutize(page_html, repo, sha):
    """Relative links and images in a README point into the repo at the pinned commit."""
    def fix(match):
        attr, url = match.group(1), match.group(2)
        if re.match(r"([a-z][a-z0-9+.-]*:|#|/)", url, re.I):
            return match.group(0)
        base = f"https://raw.githubusercontent.com/{repo}/{sha}/" if attr == "src" else f"https://github.com/{repo}/blob/{sha}/"
        return f'{attr}="{base}{url.lstrip("./")}"'
    return re.sub(r'(src|href)="([^"]+)"', fix, page_html)


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


def load_projects(site):
    projects = []
    listing = git("config", "-f", ".gitmodules", "--get-regexp", r"^submodule\..*\.path$") if (ROOT / ".gitmodules").exists() else ""
    for line in listing.splitlines():
        key, path = line.split(" ", 1)
        name = key[len("submodule."):-len(".path")]
        url = git("config", "-f", ".gitmodules", f"submodule.{name}.url").removesuffix(".git")
        repo = url.split("github.com/")[-1]
        folder = ROOT / path
        slug = folder.name
        full_sha = git("rev-parse", "HEAD", cwd=folder)
        sha = full_sha[:7]
        date = datetime.strptime(git("log", "-1", "--format=%cs", cwd=folder), "%Y-%m-%d")
        readme_path = folder / "README.md"
        readme = readme_path.read_text() if readme_path.exists() else ""
        title, lede, body = split_readme(readme)
        notes_dir = ROOT / "notes" / slug
        notes = (notes_dir / "notes.md").read_text() if (notes_dir / "notes.md").exists() else ""
        log = (notes_dir / "log.md").read_text() if (notes_dir / "log.md").exists() else ""
        projects.append({
            "slug": slug, "repo": repo, "url": url, "sha": sha, "date": date,
            "readme": readme, "title": title or slug, "has_title": bool(title), "lede": lede, "body": body,
            "notes": notes, "log": log,
            "source_url": f"{url}/tree/{full_sha}",
            "page_url": f"{site['url']}/{slug}/",
            "md_abs": f"{site['url']}/{slug}.md",
        })
    projects.sort(key=lambda p: p["date"], reverse=True)
    return projects


def twin(p):
    """The page as markdown: what Copy for LLM copies and what agents fetch."""
    head = f"<!-- source: {p['source_url']} | last updated: {p['date']:%Y-%m-%d} | page: {p['page_url']} -->"
    parts = [head, p["readme"].strip()]
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

    base = (TPL / "base.html").read_text()
    host = site["url"].split("//")[-1]
    first, _, rest = host.partition(".")
    brand = f"{esc(first)}<i>.</i>{esc(rest)}" if rest else esc(host)

    # home
    rows = []
    for p in projects:
        rows.append(
            f'    <a class="row" href="/{p["slug"]}/" data-spy="{esc(p["title"])}">'
            f'<span class="mono when">{p["date"]:%b %d, %Y}</span>'
            f'<span><span class="t">{esc(p["title"])}</span><span class="d">{inline(p["lede"])}</span></span>'
            f'<span class="arr">→</span></a>'
        )
    for _ in range(site.get("blanks", 0)):
        rows.append(
            '    <div class="row blank"><span class="mono when">—</span>'
            f'<span><span class="t">{esc(site.get("blank_title", "Next project"))}</span>'
            f'<span class="d">{esc(site.get("blank_text", "Write-up in progress."))}</span></span><span></span></div>'
        )
    home = fill((TPL / "home.html").read_text(), name=esc(site["name"]), tagline=esc(site["tagline"]), rows="\n".join(rows))
    (OUT / "index.html").write_text(fill(
        base, title=esc(site["name"]), description=esc(site["tagline"]), md_url="/llms.txt",
        brand=brand, github=esc(site["github"]), body=home))

    # articles and their markdown twins
    article = (TPL / "article.html").read_text()
    for p in projects:
        prompt = f"Read {p['md_abs']} and summarize this project."
        page = fill(
            article,
            title=esc(p["title"]), standfirst=inline(p["lede"]), repo=esc(p["repo"]),
            updated=f"{p['date']:%b %d, %Y}", sha=p["sha"],
            minutes=str(max(1, round(len(p["readme"].split()) / WORDS_PER_MINUTE))),
            source_url=esc(p["source_url"]), slug=p["slug"],
            claude_url="https://claude.ai/new?q=" + quote(prompt),
            page_url=esc(p["page_url"]), md_abs=esc(p["md_abs"]),
            content=absolutize(render(p["body"]), p["repo"], p["sha"]),
        )
        (OUT / p["slug"]).mkdir()
        (OUT / p["slug"] / "index.html").write_text(fill(
            base, title=f"{esc(p['title'])} · {esc(site['name'])}", description=esc(p["lede"]),
            md_url=f"/{p['slug']}.md", brand=brand, github=esc(site["github"]), body=page))
        (OUT / f"{p['slug']}.md").write_text(twin(p))

    # llms.txt and llms-full.txt
    index = [f"# {site['name']}", "", f"> {site['tagline']}", "",
             "Each project page is built from its own GitHub repo at a pinned commit. "
             "Every page has a markdown twin at the same URL with `.md`.", "", "## Projects", ""]
    index += [f"- [{p['title']}]({p['md_abs']}): {p['lede']}" for p in projects]
    index += ["", "## Source", "", f"- [This site's repo]({site['repo']}): `git clone --recursive {site['repo']}` gets every project at its pinned commit",
              f"- [Everything in one file]({site['url']}/llms-full.txt)", ""]
    (OUT / "llms.txt").write_text("\n".join(index))
    full = [f"# {site['name']}", "", f"> {site['tagline']}", ""] + [twin(p) for p in projects]
    (OUT / "llms-full.txt").write_text("\n".join(full))
    return site, projects


def check(projects):
    errors, warnings = [], []
    for p in projects:
        s = p["slug"]
        if not p["readme"]:
            errors.append(f"{s}: no README.md")
            continue
        if not p["has_title"]:
            errors.append(f"{s}: README has no title (a first line starting with '# ')")
        if not (OUT / f"{s}.md").exists():
            errors.append(f"{s}: no markdown twin was built")
        if not p["notes"]:
            errors.append(f"{s}: notes/{s}/notes.md is missing")
        newest = next((l for l in p["log"].splitlines() if l.strip() and not l.startswith("#")), "")
        if p["sha"] not in newest:
            errors.append(f"{s}: pinned at {p['sha']} but the newest line of notes/{s}/log.md does not name it; run /sync")
        # ARTICLES.md rules: warn, never block.
        if not p["lede"]:
            warnings.append(f"{s}: the README does not open with one standalone sentence")
        before_sections = p["lede"] + "\n" + p["body"].split("\n## ")[0]
        if not re.search(r"\d", re.sub(r"`[^`]*`", "", before_sections)):
            warnings.append(f"{s}: no number before the first section")
        if not re.search(r"!\[[^\]]*\]\(|<img\b|```mermaid", p["readme"]):
            warnings.append(f"{s}: no visual in the README")
        elif re.search(r"!\[\]\(", p["readme"]):
            warnings.append(f"{s}: an image has no alt text")
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
