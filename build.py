#!/usr/bin/env python3
"""Build the MoistLab site: src/ -> docs/ (GitHub Pages serves docs/).

  src/posts/YYYY-MM-DD-slug.md   notes (files starting with _ are templates and are skipped)
  src/pages/about.md             plain pages
  src/assets/                    css, fonts, images (copied as is)

A post or page starts with `key: value` lines (title, summary, date) and a blank line, then Markdown.
Run: python3 build.py   (needs the `markdown` package). Then commit and push; Pages publishes docs/.
Paths in pages are relative, so the site also works from github.io/<repo>/ before the domain resolves.
"""
import datetime as dt
import html
import re
import shutil
from pathlib import Path

import markdown

ROOT = Path(__file__).parent
SRC, OUT = ROOT / "src", ROOT / "docs"
SITE = "https://moistlab.dev"
NAME = "MoistLab"
DESC = "Notes on learning IT security: the goal, the steps, the snag, and what to do next time."
GITHUB = "https://github.com/Moistnutmeg"
BANNER_ALT = "MoistRex, a pixel dinosaur in a hoodie and sunglasses beside a glowing terminal, next to the word MoistLab"

LAYOUT = """<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#494949">
<link rel="canonical" href="{canon}">
<link rel="icon" type="image/png" sizes="32x32" href="{r}assets/img/moistrex-32.png">
<link rel="apple-touch-icon" href="{r}assets/img/moistrex-180.png">
<link rel="alternate" type="application/atom+xml" title="{name}" href="{r}feed.xml">
<link rel="preload" href="{r}assets/fonts/JetBrainsMono-Regular.woff2" as="font" type="font/woff2" crossorigin>
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{site}/assets/img/moistlab-banner-1200.jpg">
<meta property="og:type" content="{ogtype}">
<link rel="stylesheet" href="{r}assets/site.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<a class="banner" href="{r}" aria-label="{name}, home"><img src="{r}assets/img/moistlab-banner-1200.jpg" srcset="{r}assets/img/moistlab-banner-1200.jpg 1200w, {r}assets/img/moistlab-banner.jpg 2400w" sizes="(min-width: 1200px) 1200px, 100vw" width="2400" height="490" alt="{banner_alt}"></a>
<div class="wrap">
<p class="prompt" aria-hidden="true"><span class="who">moistnutmeg@moistlab:</span>~$ <span class="cmd" style="--n:{cmdlen}">{cmd}</span></p>
<nav aria-label="Main"><a href="{r}"{cur_home}>notes/</a><a href="{r}about/"{cur_about}>about.md</a><a href="{r}feed.xml">feed.xml</a></nav>
<main id="main">
{body}
</main>
</div>
<footer><div class="wrap"><a href="{github}">github</a><span>moistlab.dev</span></div><div class="wrap"><p class="prompt waiting" aria-hidden="true"><span class="who">moistnutmeg@moistlab:</span>~$ <span class="cur"></span></p></div></footer>
</body>
</html>
"""

md = markdown.Markdown(extensions=["fenced_code", "tables", "sane_lists"], output_format="html")


def parse(path):
    """Leading `key: value` lines, a blank line, then Markdown."""
    head, _, body = path.read_text(encoding="utf-8").partition("\n\n")
    meta = {}
    for line in head.splitlines():
        k, _, v = line.partition(":")
        meta[k.strip().lower()] = v.strip()
    md.reset()
    return meta, md.convert(body)


def page(out_path, depth, title, desc, body, canon_path, current="", ogtype="website", cmd="ls notes/"):
    r = "../" * depth
    text = LAYOUT.format(
        title=html.escape(title), desc=html.escape(desc), canon=SITE + canon_path, r=r, name=NAME, site=SITE,
        ogtype=ogtype, banner_alt=html.escape(BANNER_ALT), github=GITHUB, body=body, cmd=html.escape(cmd), cmdlen=len(cmd),
        cur_home=' aria-current="page"' if current == "home" else "",
        cur_about=' aria-current="page"' if current == "about" else "",
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")


def load_posts():
    posts = []
    for p in sorted((SRC / "posts").glob("*.md")):
        if p.name.startswith("_"):
            continue
        meta, content = parse(p)
        m = re.match(r"(\d{4}-\d{2}-\d{2})-(.+)\.md$", p.name)
        date = meta.get("date") or (m.group(1) if m else "")
        slug = m.group(2) if m else p.stem
        if not meta.get("title") or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
            raise SystemExit(f"{p.name}: needs a title and a YYYY-MM-DD date (in the file name or a date: line)")
        posts.append({"title": meta["title"], "summary": meta.get("summary", ""), "date": date, "slug": slug, "html": content})
    return sorted(posts, key=lambda x: x["date"], reverse=True)


def fmt(date):
    d = dt.date.fromisoformat(date)
    return f"{d.day} {d.strftime('%b %Y')}"


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SRC / "assets", OUT / "assets")
    (OUT / "CNAME").write_text("moistlab.dev")  # no newline: matches the file GitHub itself writes
    (OUT / ".nojekyll").write_text("")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")

    posts = load_posts()
    urls = ["/", "/about/"] + [f"/notes/{p['slug']}/" for p in posts]

    # home: the list of notes
    if posts:
        items = "\n".join(
            f'<li><time datetime="{p["date"]}">{fmt(p["date"])}</time><a class="t" href="notes/{p["slug"]}/">{html.escape(p["title"])}</a>'
            + (f'<span class="s">{html.escape(p["summary"])}</span>' if p["summary"] else "") + "</li>"
            for p in posts)
        listing = f'<ul class="notes">\n{items}\n</ul>'
    else:
        listing = '<p class="empty">No notes yet. The first write-up lands here.</p>'
    body = f"<h1>Notes from the lab</h1>\n<p>{html.escape(DESC)}</p>\n{listing}"
    page(OUT / "index.html", 0, NAME, DESC, body, "/", current="home", cmd="ls notes/")

    # notes
    for p in posts:
        body = (f'<h1>{html.escape(p["title"])}</h1>\n<p class="meta"><time datetime="{p["date"]}">{fmt(p["date"])}</time></p>\n{p["html"]}')
        page(OUT / "notes" / p["slug"] / "index.html", 2, f'{p["title"]} - {NAME}', p["summary"] or DESC, body,
             f'/notes/{p["slug"]}/', current="home", ogtype="article", cmd=f'cat notes/{p["slug"]}.md')

    # pages
    for f in sorted((SRC / "pages").glob("*.md")):
        meta, content = parse(f)
        page(OUT / f.stem / "index.html", 1, f'{meta.get("title", f.stem)} - {NAME}', meta.get("summary", DESC), content,
             f"/{f.stem}/", current=f.stem, cmd=f"cat {f.stem}.md")

    # 404 uses absolute asset paths because it is served from any depth
    notfound = ('<h1>Page not found</h1>\n<p>That address does not exist. The <a href="/">list of notes</a> is the place to start.</p>')
    page(OUT / "404.html", 0, f"Not found - {NAME}", DESC, notfound, "/404.html", cmd="cd missing")
    t = (OUT / "404.html").read_text().replace('"assets/', '"/assets/').replace('href=""', 'href="/"').replace('href="about/"', 'href="/about/"').replace('href="feed.xml"', 'href="/feed.xml"').replace('href="notes/', 'href="/notes/')
    (OUT / "404.html").write_text(t)

    # sitemap and atom feed
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                     + "".join(f"<url><loc>{SITE}{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    updated = (posts[0]["date"] if posts else dt.date.today().isoformat()) + "T00:00:00Z"
    entries = "".join(
        f'<entry><title>{html.escape(p["title"])}</title><link href="{SITE}/notes/{p["slug"]}/"/><id>{SITE}/notes/{p["slug"]}/</id>'
        f'<updated>{p["date"]}T00:00:00Z</updated><summary>{html.escape(p["summary"])}</summary></entry>\n' for p in posts)
    (OUT / "feed.xml").write_text(f'<?xml version="1.0" encoding="utf-8"?>\n<feed xmlns="http://www.w3.org/2005/Atom"><title>{NAME}</title>'
                                  f'<link href="{SITE}/"/><link rel="self" href="{SITE}/feed.xml"/><id>{SITE}/</id><updated>{updated}</updated>\n{entries}</feed>\n')
    print(f"built {len(posts)} note(s), {len(list((SRC / 'pages').glob('*.md')))} page(s) into docs/")


if __name__ == "__main__":
    main()
