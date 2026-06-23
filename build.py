#!/usr/bin/env python3
"""
Static generator for estudely.com.

Replicates Bear Blog's default theme (https://bearblog.dev) so the site can be
hosted on GitHub Pages. Reads markdown from content/, renders it into the Bear
Blog HTML skeleton (templates/base.html) using the estudely.com stylesheet, and
writes static files to public/.

    content/pages/home.md    -> index.html              (site landing page)
    content/pages/<slug>.md  -> <slug>/index.html       (standalone pages)
    content/posts/<slug>.md  -> <slug>/index.html       (blog posts, listed at /blog/)

Output is a faithful structural copy of Bear Blog: flat /slug/ permalinks, the
ul.blog-posts listing, <time> date tags, an Atom feed at /feed.xml, a sitemap at
/sitemap.xml, and robots.txt.

Per-post frontmatter supported:
    title, date (ISO 8601), slug, description (optional; auto-derived if absent),
    og_image (optional), draft (true|false).
"""
import html
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

import markdown
from pygments.formatters import HtmlFormatter

ROOT = Path(__file__).parent
OUT = ROOT / "public"

# ---- site config (mirrors the Bear Blog dashboard settings for estudely) ----
DOMAIN = "https://estudely.com"
SITE_TITLE = "Estudely"
SITE_AUTHOR = "Aman Verasia"
DESCRIPTION = (
    "This is the blogsite for Estudely; A Community of people who are "
    "interested in learning tech."
)
LANG = "en"
DEFAULT_THEME = "default"
THEMES = [
    ("default", "Default"),
    ("solarized", "Solarized"),
    ("dracula", "Dracula"),
    ("nord", "Nord"),
    ("rose-pine", "Rosé Pine"),
    ("terminal", "Terminal"),
    ("serif", "Serif"),
    ("contrast", "Contrast"),
    ("minimal", "Minimal"),
]
# nav items: (label, href)
NAV = [
    ("Home", "/"),
    ("Blog", "/blog/"),
    ("AI Conversations", "/ai-conversations/"),
    ("About Me", "/about-me/"),
    ("Join Community", "/join-us/"),
    ("RSS feed", "/feed.xml"),
    ("Supabase", "/supabase/"),
]

MD = markdown.Markdown(
    extensions=["extra", "sane_lists", "toc", "codehilite"],
    extension_configs={
        "toc": {"permalink": False},
        "codehilite": {"guess_lang": True, "css_class": "codehilite"},
    },
)


def parse_frontmatter(text):
    """Minimal `key: value` frontmatter parser (no PyYAML dependency)."""
    if text.startswith("---\n"):
        _, fm, body = text.split("---\n", 2)
        meta = {}
        for line in fm.strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        return meta, body.strip()
    return {}, text.strip()


def render_md(text):
    MD.reset()
    return MD.convert(text)


def fmt_date(iso):
    """Bear Blog's default date format 'd M, Y' -> e.g. '07 Mar, 2025'."""
    try:
        return datetime.fromisoformat(iso).strftime("%d %b, %Y")
    except Exception:
        return iso


def truthy(value):
    return str(value).strip().lower() in ("true", "1", "yes", "on")


def resolve_url(path):
    """Make a frontmatter path (og_image) absolute against the domain."""
    path = path.strip()
    if path.startswith(("http://", "https://")):
        return path
    return DOMAIN.rstrip("/") + "/" + path.lstrip("/")


def extract_description(html_body, meta, limit=160):
    """Per-page meta description: frontmatter `description`, else first <p>."""
    if meta.get("description"):
        return meta["description"].strip()
    m = re.search(r"<p>(.*?)</p>", html_body, re.DOTALL)
    if m:
        text = re.sub(r"<[^>]+>", "", m.group(1))
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) > limit:
            text = text[:limit].rsplit(" ", 1)[0] + "\u2026"
        return text
    return DESCRIPTION


def reading_time(html_body, wpm=200):
    text = re.sub(r"<[^>]+>", " ", html_body)
    return max(1, round(len(text.split()) / wpm))


def load(base):
    """Read every .md under `base/`, returning a list of item dicts.

    Drafts are skipped entirely (never rendered, listed, fed, or sitemapped).
    """
    items = []
    for p in sorted((ROOT / base).glob("*.md")):
        meta, body = parse_frontmatter(p.read_text(encoding="utf-8"))
        if truthy(meta.get("draft")):
            continue
        body_html = render_md(body)
        items.append(
            {
                "meta": meta,
                "html": body_html,
                "slug": meta.get("slug", p.stem),
                "title": meta.get("title", p.stem),
                "date_iso": meta.get("date", ""),
                "stem": p.stem,
                "description": extract_description(body_html, meta),
                "og_image": meta.get("og_image", "").strip(),
            }
        )
    return items


def nav_html(prefix="./"):
    return " ".join(f'<a href="{prefix}{href.lstrip("/")}">{label}</a>' for label, href in NAV)


def post_nav_html(prev, nxt):
    """prev = newer post (right), nxt = older post (left)."""
    parts = ['<nav class="post-nav">']
    if nxt:  # older post -> left
        parts.append(
            f'<span class="post-nav-older">&larr; Older: '
            f'<a href="../{nxt["slug"]}/">{html.escape(nxt["title"])}</a></span>'
        )
    else:
        parts.append('<span class="post-nav-older"></span>')
    if prev:  # newer post -> right
        parts.append(
            f'<span class="post-nav-newer">Newer: '
            f'<a href="../{prev["slug"]}/">{html.escape(prev["title"])}</a> &rarr;</span>'
        )
    else:
        parts.append('<span class="post-nav-newer"></span>')
    parts.append("</nav>")
    return "\n".join(parts)


def render_page(
    *,
    title,
    og_title,
    og_type,
    canonical,
    page_type,
    main,
    path_prefix="./",
    description=None,
    og_image="",
    jsonld="",
):
    if description is None:
        description = DESCRIPTION
    if og_image:
        img = resolve_url(og_image)
        og_image_tags = (
            f'  <meta property="og:image" content="{html.escape(img)}">\n'
            f'  <meta name="twitter:card" content="summary_large_image">\n'
            f'  <meta name="twitter:image" content="{html.escape(img)}">'
        )
    else:
        og_image_tags = '  <meta name="twitter:card" content="summary">'

    tpl = (ROOT / "templates" / "base.html").read_text(encoding="utf-8")
    repl = {
        "<!--LANG-->": LANG,
        "<!--TITLE-->": html.escape(title),
        "<!--CANONICAL-->": canonical,
        "<!--DESCRIPTION-->": html.escape(description),
        "<!--SITE_TITLE-->": html.escape(SITE_TITLE),
        "<!--OG_TITLE-->": html.escape(og_title),
        "<!--OG_TYPE-->": og_type,
        "<!--PAGE_TYPE-->": page_type,
        "<!--PRE-->": path_prefix,
        "<!--NAV-->": nav_html(path_prefix),
        "<!--MAIN-->": main,
        "<!--OG_IMAGE-->": og_image_tags,
        "<!--JSONLD-->": jsonld,
        "<!--DEFAULT_THEME-->": DEFAULT_THEME,
        "<!--THEME_OPTIONS-->": "\n".join(
            f'        <option value="{val}"{" selected" if val == DEFAULT_THEME else ""}>{label}</option>'
            for val, label in THEMES
        ),
    }
    out = tpl
    for k, v in repl.items():
        out = out.replace(k, v)
    return out


def build_jsonld(p):
    data = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": p["title"],
        "datePublished": p["date_iso"],
        "dateModified": p["date_iso"],
        "author": {"@type": "Person", "name": SITE_AUTHOR},
        "publisher": {"@type": "Organization", "name": SITE_TITLE, "url": DOMAIN},
        "description": p["description"],
        "mainEntityOfPage": f"{DOMAIN}/{p['slug']}/",
    }
    if p["og_image"]:
        data["image"] = resolve_url(p["og_image"])
    return '<script type="application/ld+json">' + json.dumps(data) + "</script>"


def write(rel, content):
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def build_feed(posts):
    last = posts[0]["date_iso"] if posts else datetime.now(timezone.utc).isoformat()
    entries = []
    for p in posts:
        entries.append(
            "  <entry>\n"
            f"    <id>{DOMAIN}/{p['slug']}/</id>\n"
            f"    <title>{html.escape(p['title'])}</title>\n"
            f"    <updated>{p['date_iso']}</updated>\n"
            f"    <author><name>{html.escape(SITE_TITLE)}</name></author>\n"
            f"    <link href=\"{DOMAIN}/{p['slug']}/\" rel=\"alternate\"/>\n"
            f"    <published>{p['date_iso']}</published>\n"
            f"    <summary>{html.escape(p['description'])}</summary>\n"
            f"    <content type=\"html\">{html.escape(p['html'])}</content>\n"
            "  </entry>"
        )
    return (
        "<?xml version='1.0' encoding='UTF-8'?>\n"
        '<feed xmlns="http://www.w3.org/2005/Atom">\n'
        f"  <id>{DOMAIN}</id>\n"
        f"  <title>{html.escape(SITE_TITLE)}</title>\n"
        f"  <updated>{last}</updated>\n"
        f"  <author><name>{html.escape(SITE_TITLE)}</name></author>\n"
        f'  <link href="{DOMAIN}/" rel="alternate"/>\n'
        f'  <link href="{DOMAIN}/feed.xml" rel="self"/>\n'
        f"  <subtitle>{html.escape(DESCRIPTION)}</subtitle>\n"
        + "\n".join(entries)
        + "\n</feed>\n"
    )


def build_sitemap(pages, posts):
    urls = [(f"{DOMAIN}/", None), (f"{DOMAIN}/blog/", None)]
    for pg in pages:
        if pg["slug"] != "home":
            urls.append((f"{DOMAIN}/{pg['slug']}/", pg.get("date_iso") or None))
    for p in posts:
        urls.append((f"{DOMAIN}/{p['slug']}/", p["date_iso"] or None))
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for loc, lastmod in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{loc}</loc>")
        if lastmod:
            lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def generate_pygments_css():
    """Two Pygments themes scoped to .codehilite; site switches via media query."""
    light = HtmlFormatter(style="default").get_style_defs(".codehilite")
    dark = HtmlFormatter(style="monokai").get_style_defs(".codehilite")
    return light, dark


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    # static assets (style.css, favicon files, etc.) -> /static/
    if (ROOT / "static").exists():
        shutil.copytree(ROOT / "static", OUT / "static")
    # CNAME file (custom domain, required by GitHub Pages)
    if (ROOT / "CNAME").exists():
        shutil.copy2(ROOT / "CNAME", OUT / "CNAME")
    # theme CSS files (copied from themes/ dir so the JS picker can swap them)
    if (ROOT / "themes").exists():
        shutil.copytree(ROOT / "themes", OUT / "themes")

    # syntax-highlighting themes (generated per build so no manual step)
    light_css, dark_css = generate_pygments_css()
    write("static/syntax-light.css", light_css)
    write("static/syntax-dark.css", dark_css)

    pages = load("content/pages")
    posts = load("content/posts")
    posts.sort(key=lambda i: i["date_iso"], reverse=True)

    # ---- home (landing) — includes recent posts list (Bear Blog layout) ----
    home = next((p for p in pages if p["slug"] == "home"), None)
    home_rows = [
        '<li data-tags="">'
        f'<span><i><time datetime="{p["date_iso"]}">'
        f'{fmt_date(p["date_iso"])}</time></i></span>'
        f'<a href="{p["slug"]}/">{html.escape(p["title"])}</a>'
        "</li>"
        for p in posts
    ]
    home_main = (home["html"] if home else "<p>No posts yet</p>")
    home_main += '\n<ul class="blog-posts">\n' + "\n".join(home_rows) + "\n</ul>"
    write(
        "index.html",
        render_page(
            title=SITE_TITLE,
            og_title=SITE_TITLE,
            og_type="website",
            canonical=f"{DOMAIN}/",
            page_type="home",
            main=home_main,
            description=DESCRIPTION,
        ),
    )

    # ---- pages (everything except home) ----
    for pg in pages:
        if pg["slug"] == "home":
            continue
        slug = pg["slug"]
        write(
            f"{slug}/index.html",
            render_page(
                title=f"{pg['title']} | {SITE_TITLE}",
                og_title=pg["title"],
                og_type="website",
                canonical=f"{DOMAIN}/{slug}/",
                page_type="page",
                main=pg["html"],
                path_prefix="../",
                description=pg["description"],
                og_image=pg["og_image"],
            ),
        )

    # ---- posts ----
    for i, p in enumerate(posts):
        slug = p["slug"]
        rt = reading_time(p["html"])
        newer = posts[i - 1] if i > 0 else None
        older = posts[i + 1] if i < len(posts) - 1 else None
        main_html = (
            f'<h1>{html.escape(p["title"])}</h1>\n'
            f'<p><i><time datetime="{p["date_iso"]}">'
            f'{fmt_date(p["date_iso"])}</time> &middot; {rt} min read</i></p>\n'
            f'{p["html"]}\n'
            f'{post_nav_html(newer, older)}'
        )
        write(
            f"{slug}/index.html",
            render_page(
                title=f"{p['title']} | {SITE_TITLE}",
                og_title=p["title"],
                og_type="article",
                canonical=f"{DOMAIN}/{slug}/",
                page_type="post",
                main=main_html,
                path_prefix="../",
                description=p["description"],
                og_image=p["og_image"],
                jsonld=build_jsonld(p),
            ),
        )

    # ---- blog listing (ul.blog-posts, newest first) ----
    rows = [
        '<li data-tags="">'
        f'<span><i><time datetime="{p["date_iso"]}">'
        f'{fmt_date(p["date_iso"])}</time></i></span>'
        f'<a href="../{p["slug"]}/">{html.escape(p["title"])}</a>'
        "</li>"
        for p in posts
    ]
    write(
        "blog/index.html",
        render_page(
            title=f"Blog | {SITE_TITLE}",
            og_title="Blog",
            og_type="website",
            canonical=f"{DOMAIN}/blog/",
            page_type="blog",
            main='<ul class="blog-posts">\n' + "\n".join(rows) + "\n</ul>",
            path_prefix="../",
        ),
    )

    # ---- atom feed, sitemap, robots ----
    write("feed.xml", build_feed(posts))
    write("sitemap.xml", build_sitemap(pages, posts))
    write(
        "robots.txt",
        f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n",
    )

    html_count = sum(1 for _ in OUT.rglob("*.html"))
    print(f"Built {html_count} HTML page(s) + feed.xml + sitemap.xml into {OUT}/")
    print(f"  pages: {[p['slug'] for p in pages]}")
    print(f"  posts: {len(posts)} ({posts[0]['slug']} ... {posts[-1]['slug']})" if posts else "  posts: 0")


if __name__ == "__main__":
    main()
