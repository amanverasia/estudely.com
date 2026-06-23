# Estudely — Astro Rebuild Design

**Date:** 2026-06-23
**Branch:** `astro-rebuild`
**Status:** Approved (design + mockups)

## Goal

Rebuild estudely.com from the ground up as a minimal, terminal-inspired
cybersecurity blog using Astro, deployed statically to GitHub Pages on the
existing custom domain (`estudely.com`). Replaces the current Python
(Bear Blog-style) static generator.

## Scope

- Fresh Astro build on the `astro-rebuild` branch.
- Wire the existing 8 markdown posts into Astro's content system so they build,
  but content polish is deferred. Design and structure are the focus now.
- Branding stays **Estudely** (consistent with the YouTube channel), with bio
  and links sourced from the existing about-me content.

## Approach

Astro with built-in **Content Collections** (type-safe markdown via Zod),
`@astrojs/sitemap`, `@astrojs/rss`, and Shiki for syntax highlighting (built in).
Static output, no `base` path (custom-domain root deploy). Chosen over a
pre-made blog theme (too much to strip out) and MDX (YAGNI — plain markdown
posts, no React islands needed yet; can add later without rework).

## Architecture

```
/  (repo root, astro-rebuild branch)
├── astro.config.mjs        # site: https://estudely.com, sitemap integration
├── package.json
├── tsconfig.json
├── src/
│   ├── content/
│   │   ├── config.ts        # blog collection w/ Zod schema
│   │   └── blog/            # markdown posts
│   ├── layouts/
│   │   ├── BaseLayout.astro  # html shell, SEO head, no-flash theme script
│   │   └── PostLayout.astro  # single-post chrome
│   ├── components/
│   │   ├── Header.astro
│   │   ├── Footer.astro
│   │   ├── PostCard.astro
│   │   └── ThemeToggle.astro
│   ├── pages/
│   │   ├── index.astro        # Home: hero + recent posts
│   │   ├── blog/index.astro   # full post list
│   │   ├── blog/[...slug].astro
│   │   ├── about.astro
│   │   ├── 404.astro
│   │   └── rss.xml.js
│   ├── styles/global.css      # CSS custom-property theme tokens
│   └── utils/readingTime.ts
└── public/                    # CNAME, favicon, og image, robots.txt
```

## Content Model

Blog collection schema (`src/content.config.ts`, Astro Content Layer with glob loader):

| Field        | Type      | Notes                                              |
|--------------|-----------|----------------------------------------------------|
| `title`      | string    | required                                           |
| `date`       | date      | required; used for sort + display                  |
| `description`| string    | optional; falls back to generated excerpt for SEO  |
| `tags`       | string[]  | default `[]`                                       |
| `draft`      | boolean   | default `false`; drafts excluded from prod builds  |

Data flow:
- Home: latest 5 non-draft posts, sorted by date desc.
- Blog index: all non-draft posts, sorted by date desc.
- Reading time: computed at build from word count via `utils/readingTime.ts`
  (no heavy dependency).
- About page: hand-built from existing about-me content (bio, quick facts,
  social links: YouTube/Estudely, GitHub, LinkedIn, BlueSky, Instagram).

## Visual Design (terminal-inspired minimal)

- **Layout:** single centered column (~680px), generous vertical rhythm,
  no sidebar.
- **Type:** JetBrains Mono for headings/nav/meta/code; Inter (with system
  fallback) for body prose.
- **Color (dark-first):** near-black bg (`#0b0e14`), off-white text, one muted
  cyan accent (`#4fd6be`) plus a soft blue (`#82aaff`) for links/tags. Light
  mode is a warm paper inverse using the same tokens.
- **Cyber cues (subtle):** `~/estudely $` brand prompt, blinking accent cursor,
  `// section` and `# heading` mono prefixes, `cat blog/* →` and `cd ..` CTAs.
  No ASCII walls or fake window chrome.
- **Theme toggle:** `☾`/`☀` in nav, persisted to `localStorage`, with an inline
  no-flash script in `<head>` that applies the stored theme before paint.
- **Post styling:** mono title, `// date · reading time · tags` meta line,
  Shiki dark code blocks matching the site, `#tag` pills.

## SEO, Feeds & Errors

- Per-page `<title>`, meta description, canonical, Open Graph + Twitter card
  tags via BaseLayout.
- `sitemap-index.xml` via `@astrojs/sitemap`; `rss.xml` feed via `@astrojs/rss`.
- Custom `404.astro` styled as a terminal `command not found` with a home link.

## Deployment

- Replace `.github/workflows/deploy.yml` with an Astro build pipeline:
  `npm ci && npm run build`, upload `dist/` via `actions/upload-pages-artifact`,
  deploy via `actions/deploy-pages`.
- `public/CNAME` contains `estudely.com` so it lands in `dist/` and Pages keeps
  the custom domain.
- Existing Python generator files (`build.py`, `templates/`, `themes/`,
  `static/`, current `public/`) to be removed/replaced as part of the rebuild,
  since this branch is a clean replacement.

## Testing & Verification

Static site verification:
1. `npm run build` completes with zero errors.
2. `astro check` passes (type-safe content collections).
3. `npm run preview` smoke test of every route: `/`, `/blog`, a post,
   `/about`, `/404`, `/rss.xml`, `/sitemap-index.xml`.

Build must be confirmed clean before the work is declared done.

## Out of Scope (for now)

- Content/copy polish of the 9 migrated posts.
- Tag filtering/index pages, search, comments, analytics.
- MDX / interactive post components.
- A Projects/Now page.
