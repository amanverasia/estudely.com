# estudely.com

A static, GitHub Pages–hosted replica of the [Estudely](https://estudely.com)
blog, faithfully reproducing [Bear Blog](https://bearblog.dev)'s default theme.
The content lives in plain Markdown; `build.py` renders it into the Bear Blog
HTML skeleton and pushes the result to GitHub Pages automatically on every push.

## Layout

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

## Editing

- **New post:** drop a file in `content/posts/my-post.md`:
  ```markdown
  ---
  title: My Post
  date: 2026-06-23T10:00:00+00:00
  slug: my-post
  ---

  Write your post in Markdown here.
  ```
- **New page:** same idea in `content/pages/`, then link it from `NAV` in `build.py`.
- Commit and push — the workflow rebuilds and deploys automatically.

## Run locally

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python build.py      # writes ./public/
python -m http.server -d public 8000   # preview at http://localhost:8000
```

## Custom domain (estudely.com)

This repo ships a `CNAME` so GitHub Pages expects `estudely.com`. To make the
domain resolve here:

1. GitHub repo → **Settings → Pages** → set **Source** to *GitHub Actions*.
2. In your DNS provider, point `estudely.com` at GitHub Pages:
   - **A records** for the apex: `185.199.108.153`, `109`, `110`, `111`
   - (optional) `www` → `amanverasia.github.io.` as a CNAME.
3. Until DNS is repointed, the site is live at
   `https://amanverasia.github.io/estudely.com/` (note: internal links are
   root-relative, so they resolve correctly once the apex domain is active).

## Notes on fidelity

- The theme is Bear Blog's stock `default.css`; the only deviation from upstream
  is `--width: 720px` (matches the live site).
- **Email subscribe form:** Bear Blog's form needs a backend; GitHub Pages is
  static. The form is kept *visually identical* but submit is handled
  client-side with a friendly message. To collect real subscribers, wire
  `estudelySubscribe()` in `build.py` to a service (Buttondown, Formspree,
  ConvertKit, etc.).
- Bear Blog's analytics/upvote widgets are server-side features and are not
  reproduced (they require a backend). RSS is reproduced at `/feed.xml`.
