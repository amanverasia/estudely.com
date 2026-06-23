#!/usr/bin/env python3
"""
Static generator for estudely.com.

Replicates Bear Blog's default theme (https://bearblog.dev) so the site can be
hosted on GitHub Pages. Reads markdown from content/, renders it into the Bear
Blog HTML skeleton (templates/base.html) using the estudely.com stylesheet, and
writes static files to public/.

    content/home.md          -> index.html              (site landing page)
    content/pages/<slug>.md  -> <slug>/index.html       (standalone pages)
    content/posts/<slug>.md  -> <slug>/index.html       (blog posts, listed at /blog/)

The published output is a faithful structural copy of Bear Blog: flat /slug/
permalinks, the ul.blog-posts listing, <time> date tags, the email-subscribe
footer, and an Atom feed at /feed.xml.
"""
import html
import shutil
from datetime import datetime, timezone
from pathlib import Path

import markdown

ROOT = Path(__file__).parent
OUT = ROOT / "public"

# ---- site config (mirrors the Bear Blog dashboard settings for estudely) ----
DOMAIN = "https://estudely.com"
SITE_TITLE = "Estudely"
DESCRIPTION = (
    "This is the blogsite for Estudely; A Community of people who are "
    "interested in learning tech.\n\nSubscribe to my blog via email or "
    "RSS feed...."
)
LANG = "en"
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
    extensions=["extra", "sane_lists", "toc"],
    extension_configs={"toc": {"permalink": False}},
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


def load(base):
    items = []
    for p in sorted((ROOT / base).glob("*.md")):
        meta, body = parse_frontmatter(p.read_text(encoding="utf-8"))
        items.append(
            {
                "meta": meta,
                "html": render_md(body),
                "slug": meta.get("slug", p.stem),
                "title": meta.get("title", p.stem),
                "date_iso": meta.get("date", ""),
                "stem": p.stem,
            }
        )
    return items


def nav_html(prefix="./"):
    return " ".join(f'<a href="{prefix}{href.lstrip("/")}">{label}</a>' for label, href in NAV)


# Footer subscribe form. Bear Blog's original POSTs to /email-subscribe/ (a
# backend that does not exist on static hosting). This replica keeps the form
# visually identical but handles submit gracefully client-side. Wire it to a
# real provider (Buttondown/Formspree) by replacing estudelySubscribe().
FOOTER_FORM = """<h4 id="subscribe-to-my-blog">Subscribe to my blog</h4>
<form class="email-signup" onsubmit="return estudelySubscribe(event)">
  <input type="text" name="name" autocomplete="off" style="display:none">
  <input type="email" placeholder="Email address..." name="email" required
         autocomplete="off" style="background-color:#eceff4;padding:5px">
  <br>
  <input type="submit" value="Subscribe">
</form>
<p id="signup-msg" style="font-style:italic"></p>
<script>
function estudelySubscribe(e){
  e.preventDefault();
  var f=e.target, msg=document.getElementById('signup-msg');
  msg.textContent='Thanks! Email subscriptions are not active on this mirror yet \\u2014 please use the RSS feed.';
  f.reset();
  return false;
}
</script>"""


def render_page(*, title, og_title, og_type, canonical, page_type, main, path_prefix="./"):
    tpl = (ROOT / "templates" / "base.html").read_text(encoding="utf-8")
    repl = {
        "<!--LANG-->": LANG,
        "<!--TITLE-->": html.escape(title),
        "<!--CANONICAL-->": canonical,
        "<!--DESCRIPTION-->": html.escape(DESCRIPTION),
        "<!--SITE_TITLE-->": html.escape(SITE_TITLE),
        "<!--OG_TITLE-->": html.escape(og_title),
        "<!--OG_TYPE-->": og_type,
        "<!--PAGE_TYPE-->": page_type,
        "<!--PRE-->": path_prefix,
        "<!--NAV-->": nav_html(path_prefix),
        "<!--MAIN-->": main,
        "<!--FOOTER_FORM-->": FOOTER_FORM,
    }
    out = tpl
    for k, v in repl.items():
        out = out.replace(k, v)
    return out


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


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    # static assets (style.css, favicon files, etc.) -> /static/
    if (ROOT / "static").exists():
        shutil.copytree(ROOT / "static", OUT / "static")

    pages = load("content/pages")
    posts = load("content/posts")
    posts.sort(key=lambda i: i["date_iso"], reverse=True)

    # ---- home (landing) ----
    home = next((p for p in pages if p["slug"] == "home"), None)
    write(
        "index.html",
        render_page(
            title=SITE_TITLE,
            og_title=SITE_TITLE,
            og_type="website",
            canonical=f"{DOMAIN}/",
            page_type="home",
            main=home["html"] if home else "<p>No posts yet</p>",
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
            ),
        )

    # ---- posts ----
    for p in posts:
        slug = p["slug"]
        main_html = (
            f'<h1>{html.escape(p["title"])}</h1>\n'
            f'<p><i><time datetime="{p["date_iso"]}">'
            f'{fmt_date(p["date_iso"])}</time></i></p>\n'
            f'{p["html"]}'
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

    # ---- atom feed ----
    write("feed.xml", build_feed(posts))

    html_count = sum(1 for _ in OUT.rglob("*.html"))
    print(f"Built {html_count} HTML page(s) + feed.xml into {OUT}/")
    print(f"  pages: {[p['slug'] for p in pages]}")
    print(f"  posts: {len(posts)} ({posts[0]['slug']} ... {posts[-1]['slug']})")


if __name__ == "__main__":
    main()
