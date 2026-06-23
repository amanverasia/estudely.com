# estudely.com

[![Live site](https://img.shields.io/website?up_color=%234c1&down_color=%23e05d44&down_message=offline&up_message=online&url=https%3A%2F%2Festudely.com)](https://estudely.com)

Source for the **[Estudely](https://estudely.com)** blog — notes on
cybersecurity, AI, and the occasional rabbit hole. A fast, minimal,
terminal-inspired static site built with [Astro](https://astro.build) and
hosted on GitHub Pages.

Content is plain Markdown; Astro builds it into a static site and a GitHub
Actions workflow deploys automatically on every push to `main`.

## Features

- **Static & fast** — Astro ships zero JavaScript by default.
- **Markdown content** — posts live in `src/content/blog/` as type-safe
  Content Collections.
- **Terminal-minimal theme** — single ~680px column, monospace accents, with a
  dark/light toggle (persisted, no flash on load).
- **RSS feed** at `/rss.xml` and a sitemap at `/sitemap-index.xml`.
- **Deploys itself** — push to `main`, GitHub Pages goes live within a minute.

## Layout

```
astro.config.mjs            # site config + sitemap integration
src/
  consts.ts                 # site title, description, social links
  content.config.ts         # blog Content Collection schema
  content/blog/             # blog posts (Markdown)
  styles/global.css         # theme tokens + prose styles
  layouts/                  # BaseLayout, PostLayout
  components/               # Header, Footer, ThemeToggle, PostCard
  pages/                    # index, blog/, about, 404, rss.xml
public/                     # CNAME, favicon.svg, robots.txt
.github/workflows/          # builds + deploys to Pages on push to main
```

## Run locally

You'll need Node 22+.

```bash
npm install
npm run dev        # dev server at http://localhost:4321
npm run build      # builds to ./dist
npm run preview    # preview the production build
npm run check      # type-check content + components
```

## Writing a post

Create `src/content/blog/my-post.md`:

```markdown
---
title: My Post
date: 2026-06-23T10:00:00+00:00
description: A one-line summary used for SEO and post cards.
tags: [cybersecurity, notes]
draft: false
---

Write your post in Markdown here.
```

`title` and `date` are required; `description`, `tags`, and `draft` are
optional. Set `draft: true` to exclude a post from production builds. Commit and
push to `main`; the workflow rebuilds and deploys automatically.

## Custom domain

This repo ships [`public/CNAME`](public/CNAME) so GitHub Pages serves
`estudely.com`. To point your own domain at a fork:

1. Repo **Settings → Pages → Source** = *GitHub Actions*.
2. Add DNS records at your provider:
   - **A records** (apex): `185.199.108.153`, `.109`, `.110`, `.111`
   - (optional) `www` → `<user>.github.io.` as a CNAME.
3. Update `public/CNAME` and the `site` URL in `astro.config.mjs`.

## License & content

All **blog content** under `src/content/` and the site tooling are
© Estudely / Aman Verasia — **all rights reserved**. This is a personal
website; please do not copy, redistribute, or republish any part of it.

## Links

- **Live site:** [estudely.com](https://estudely.com)
- **Built on:** [Astro](https://astro.build) · [GitHub Pages](https://pages.github.com)
