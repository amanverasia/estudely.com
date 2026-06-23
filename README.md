# estudely.com

[![Live site](https://img.shields.io/website?up_color=%234c1&down_color=%23e05d44&down_message=offline&up_message=online&url=https%3A%2F%2Festudely.com)](https://estudely.com)

Source for the **[Estudely](https://estudely.com)** blog — a tech-learning
community focused on programming, cybersecurity, and AI. This repo builds a
fast, minimal, static site that faithfully reproduces
[Bear Blog](https://bearblog.dev)'s default theme and hosts it on GitHub Pages.

Content is plain Markdown; [`build.py`](build.py) renders it into the Bear Blog
HTML skeleton and a GitHub Actions workflow deploys automatically on every push
to `main`.

## ✨ Features

- ⚡ **Static & fast** — no JavaScript frameworks, no tracking, no backend.
- ✍️ **Markdown content** — write posts in `content/posts/`, they just work.
- 🎨 **Bear Blog theme** — clean, readable, ~720px column, dark-on-light.
- 📡 **RSS feed** auto-generated at `/feed.xml`.
- 🚀 **Deploys itself** — push to `main`, GitHub Pages goes live within a minute.

## 📁 Layout

```
build.py              # static generator (markdown -> Bear Blog HTML)
templates/base.html   # Bear Blog page skeleton (header, nav, main, footer)
static/style.css      # estudely.com stylesheet (Bear Blog default, width 720px)
content/
  pages/              # standalone pages + home.md (the landing page)
  posts/              # blog posts (listed newest-first at /blog/)
.github/workflows/    # builds + deploys to Pages on push
CNAME                 # custom domain: estudely.com
```

## 🛠️ Run locally

You'll need Python 3.10+.

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python build.py                       # writes ./public/
python -m http.server -d public 8000  # preview at http://localhost:8000
```

## ✍️ Writing a post

1. Create `content/posts/my-post.md`:

   ```markdown
   ---
   title: My Post
   date: 2026-06-23T10:00:00+00:00
   slug: my-post
   ---

   Write your post in Markdown here.
   ```

2. Commit and push to `main`. The workflow rebuilds and deploys automatically.

To add a standalone (non-blog) page, drop the same front-matter file in
`content/pages/` and add it to the `NAV` list in [`build.py`](build.py).

## 🧩 How it works

- [`build.py`](build.py) reads every `.md` under `content/`, converts it to HTML
  with [python-markdown](https://python-markdown.github.io/), and slots it into
  [`templates/base.html`](templates/base.html).
- Posts are listed newest-first at `/blog/`; each gets a flat `/slug/` permalink.
- An Atom feed is generated at `/feed.xml`.
- Site config (title, description, nav, domain) lives at the top of
  [`build.py`](build.py).

## 🌐 Custom domain

This repo ships a [`CNAME`](CNAME) so GitHub Pages serves `estudely.com`. To
point your own domain at a fork:

1. Repo **Settings → Pages → Source** = *GitHub Actions*.
2. Add DNS records at your provider:
   - **A records** (apex): `185.199.108.153`, `.109`, `.110`, `.111`
   - (optional) `www` → `<user>.github.io.` as a CNAME.
3. Update the `CNAME` file and `DOMAIN` in [`build.py`](build.py).

## 📜 License & content

The **theme/HTML** (Bear Blog's `default.css` skeleton) belongs to
[Bear Blog](https://bearblog.dev) / Herman Martinus.

All **blog content** under [`content/`](content/) (posts and pages) is © Estudely
and is **not** licensed for redistribution — please don't copy the articles.
The build tooling itself is free to read, fork, and learn from.

## 🔗 Links

- 🌍 **Live site:** [estudely.com](https://estudely.com)
- 📺 **Estudely community:** programming, cybersecurity & AI education
- 🧱 **Built on:** [Bear Blog](https://bearblog.dev) · [GitHub Pages](https://pages.github.com)
