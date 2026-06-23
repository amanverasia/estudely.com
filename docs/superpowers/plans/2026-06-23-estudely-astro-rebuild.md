# Estudely Astro Rebuild Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild estudely.com as a minimal, terminal-inspired cybersecurity blog using Astro, deployed statically to GitHub Pages on the custom domain estudely.com.

**Architecture:** Astro static site using built-in Content Collections (type-safe markdown via Zod), Shiki syntax highlighting, `@astrojs/sitemap` and `@astrojs/rss`. Single centered-column layout, CSS custom-property theme tokens with a dark/light toggle. No `base` path (custom-domain root deploy).

**Tech Stack:** Astro 4+, TypeScript, Content Collections, `@astrojs/sitemap`, `@astrojs/rss`, JetBrains Mono + Inter (self-hosted via `@fontsource`).

**Verification model:** This is a static site. The test gate at each task is `npx astro check` (type/content validation) and/or `npm run build` (full build) completing with zero errors, plus route smoke tests via `npm run preview`. There are no unit-test frameworks introduced.

---

## File Structure

```
/ (repo root, astro-rebuild branch)
├── package.json              # scripts: dev, build, preview, check
├── astro.config.mjs          # site URL, sitemap integration
├── tsconfig.json             # extends astro/tsconfigs/strict
├── .gitignore                # add node_modules, dist, .astro
├── src/
│   ├── content/
│   │   ├── config.ts          # blog collection Zod schema
│   │   └── blog/              # migrated markdown posts (9)
│   ├── consts.ts             # SITE_TITLE, SITE_DESCRIPTION, SOCIALS
│   ├── utils/readingTime.ts  # word-count → minutes helper
│   ├── styles/global.css     # theme tokens + base element styles
│   ├── components/
│   │   ├── Header.astro
│   │   ├── Footer.astro
│   │   ├── ThemeToggle.astro
│   │   └── PostCard.astro
│   ├── layouts/
│   │   ├── BaseLayout.astro   # html shell, SEO head, no-flash theme script
│   │   └── PostLayout.astro   # single-post chrome
│   └── pages/
│       ├── index.astro
│       ├── about.astro
│       ├── 404.astro
│       ├── rss.xml.js
│       └── blog/
│           ├── index.astro
│           └── [...slug].astro
├── public/                    # CNAME, favicon.svg, robots.txt
└── .github/workflows/deploy.yml  # replaced: Astro build pipeline
```

---

## Task 1: Scaffold Astro project & dependencies

**Files:**
- Create: `package.json`, `astro.config.mjs`, `tsconfig.json`
- Modify: `.gitignore`

- [ ] **Step 1: Initialize package.json and install Astro + integrations**

Run from repo root (it is the `astro-rebuild` branch already):

```bash
npm init -y
npm install astro
npm install @astrojs/sitemap @astrojs/rss
npm install @fontsource-variable/jetbrains-mono @fontsource-variable/inter
```

- [ ] **Step 2: Set scripts in package.json**

Replace the `"scripts"` block in `package.json` with:

```json
"type": "module",
"scripts": {
  "dev": "astro dev",
  "build": "astro build",
  "preview": "astro preview",
  "check": "astro check"
}
```

- [ ] **Step 3: Create astro.config.mjs**

```js
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://estudely.com',
  integrations: [sitemap()],
  markdown: {
    shikiConfig: { theme: 'github-dark', wrap: true },
  },
});
```

- [ ] **Step 4: Create tsconfig.json**

```json
{
  "extends": "astro/tsconfigs/strict",
  "include": [".astro/types.d.ts", "**/*"],
  "exclude": ["dist"]
}
```

- [ ] **Step 5: Update .gitignore**

Ensure these lines exist (append if missing):

```
node_modules/
dist/
.astro/
```

- [ ] **Step 6: Verify install**

Run: `npx astro --version`
Expected: prints an Astro version number with no error.

- [ ] **Step 7: Commit**

```bash
git add package.json package-lock.json astro.config.mjs tsconfig.json .gitignore
git commit -m "chore: scaffold Astro project with integrations"
```

---

## Task 2: Site constants & content collection schema

**Files:**
- Create: `src/consts.ts`, `src/content/config.ts`

- [ ] **Step 1: Create src/consts.ts**

```ts
export const SITE_TITLE = 'Estudely';
export const SITE_DESCRIPTION =
  'Cybersecurity, AI, and the occasional rabbit hole — notes by Aman Verasia.';
export const SITE_URL = 'https://estudely.com';

export const SOCIALS = [
  { label: 'youtube', href: 'https://www.youtube.com/estudely' },
  { label: 'github', href: 'https://github.com/amanverasia' },
  { label: 'linkedin', href: 'https://www.linkedin.com/in/amanverasia' },
  { label: 'bluesky', href: 'https://bsky.app/profile/estudely.com' },
  { label: 'instagram', href: 'https://instagram.com/amanverasia' },
];
```

- [ ] **Step 2: Create src/content/config.ts**

Schema makes `description`, `tags`, `draft` optional so existing posts
(which only have `title`, `date`, `slug`) validate without edits.

```ts
import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/blog' }),
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    slug: z.string().optional(),
    description: z.string().optional(),
    tags: z.array(z.string()).default([]),
    draft: z.boolean().default(false),
  }),
});

export const collections = { blog };
```

- [ ] **Step 3: Verify schema compiles**

Run: `npx astro sync && npx astro check`
Expected: completes with 0 errors (0 hint/warning is fine). Content dir is
empty so no content errors yet.

- [ ] **Step 4: Commit**

```bash
git add src/consts.ts src/content/config.ts
git commit -m "feat: add site constants and blog content schema"
```

---

## Task 3: Migrate existing posts into the blog collection

**Files:**
- Create: `src/content/blog/*.md` (9 files copied from `content/posts/`)

- [ ] **Step 1: Copy the 9 markdown posts into the collection**

```bash
mkdir -p src/content/blog
cp content/posts/*.md src/content/blog/
ls src/content/blog
```

Expected: 9 `.md` files listed.

- [ ] **Step 2: Verify all posts validate against the schema**

Run: `npx astro sync && npx astro check`
Expected: 0 errors. (The existing `title` + `date` + `slug` frontmatter
satisfies the schema; missing fields use defaults.)

- [ ] **Step 3: Commit**

```bash
git add src/content/blog
git commit -m "feat: migrate existing posts into blog collection"
```

---

## Task 4: Global styles & theme tokens

**Files:**
- Create: `src/styles/global.css`

- [ ] **Step 1: Create src/styles/global.css**

Tokens and base styles ported from the approved mockup.

```css
:root {
  --bg: #0b0e14;
  --bg-soft: #11151f;
  --fg: #d7dce5;
  --fg-dim: #8b94a7;
  --fg-faint: #5a6376;
  --accent: #4fd6be;
  --accent-2: #82aaff;
  --border: #1d2330;
  --selection: #2a3344;
  --code-bg: #0d1117;
  --mono: 'JetBrains Mono Variable', 'JetBrains Mono', ui-monospace, monospace;
  --sans: 'Inter Variable', 'Inter', system-ui, -apple-system, sans-serif;
  --width: 680px;
}
html[data-theme='light'] {
  --bg: #faf8f3;
  --bg-soft: #f0ece2;
  --fg: #2b2b2b;
  --fg-dim: #5c5c5c;
  --fg-faint: #8a8a8a;
  --accent: #1a9e88;
  --accent-2: #3a6fd8;
  --border: #e3ddd0;
  --selection: #e0dccf;
  --code-bg: #1b1e26;
}
* { box-sizing: border-box; }
::selection { background: var(--selection); }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--fg);
  font-family: var(--sans);
  font-size: 17px;
  line-height: 1.75;
  -webkit-font-smoothing: antialiased;
  transition: background .25s ease, color .25s ease;
}
.wrap { max-width: var(--width); margin: 0 auto; padding: 0 24px; }
a { color: var(--accent-2); text-decoration: none; }
@keyframes blink { 50% { opacity: 0; } }
.cursor { color: var(--accent); animation: blink 1.1s steps(1) infinite; }

/* prose */
.prose h2 { font-family: var(--mono); font-size: 20px; margin: 40px 0 14px; letter-spacing: -.3px; }
.prose h2::before { content: '# '; color: var(--accent); }
.prose h3 { font-family: var(--mono); font-size: 17px; margin: 28px 0 12px; }
.prose p { margin: 0 0 20px; }
.prose a { border-bottom: 1px solid var(--border); }
.prose a:hover { border-color: var(--accent-2); }
.prose code { font-family: var(--mono); font-size: .85em; background: var(--bg-soft); border: 1px solid var(--border); padding: 1px 6px; border-radius: 4px; color: var(--accent); }
.prose pre { background: var(--code-bg); border: 1px solid var(--border); border-radius: 8px; padding: 18px 20px; overflow-x: auto; font-size: 13.5px; line-height: 1.6; }
.prose pre code { background: none; border: none; padding: 0; color: inherit; }
.prose blockquote { border-left: 2px solid var(--accent); margin: 24px 0; padding: 4px 0 4px 18px; color: var(--fg-dim); font-style: italic; }
.prose ul, .prose ol { margin: 0 0 20px; padding-left: 24px; }
.prose li { margin-bottom: 6px; }
.prose img { max-width: 100%; border-radius: 8px; }
```

- [ ] **Step 2: Commit**

```bash
git add src/styles/global.css
git commit -m "feat: add global theme tokens and prose styles"
```

---

## Task 5: BaseLayout with SEO head & no-flash theme script

**Files:**
- Create: `src/layouts/BaseLayout.astro`

- [ ] **Step 1: Create src/layouts/BaseLayout.astro**

```astro
---
import '@fontsource-variable/jetbrains-mono';
import '@fontsource-variable/inter';
import '../styles/global.css';
import { SITE_TITLE, SITE_DESCRIPTION } from '../consts';

interface Props {
  title?: string;
  description?: string;
}
const { title, description = SITE_DESCRIPTION } = Astro.props;
const pageTitle = title ? `${title} — ${SITE_TITLE}` : SITE_TITLE;
const canonical = new URL(Astro.url.pathname, Astro.site).toString();
---
<!doctype html>
<html lang="en" data-theme="dark">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <title>{pageTitle}</title>
    <meta name="description" content={description} />
    <link rel="canonical" href={canonical} />
    <link rel="alternate" type="application/rss+xml" title={SITE_TITLE} href="/rss.xml" />
    <meta property="og:type" content="website" />
    <meta property="og:title" content={pageTitle} />
    <meta property="og:description" content={description} />
    <meta property="og:url" content={canonical} />
    <meta name="twitter:card" content="summary_large_image" />
    <script is:inline>
      const t = localStorage.getItem('theme');
      if (t) document.documentElement.setAttribute('data-theme', t);
    </script>
  </head>
  <body>
    <slot />
  </body>
</html>
```

- [ ] **Step 2: Verify it compiles**

Run: `npx astro check`
Expected: 0 errors. (`@fontsource-variable/*` packages were installed in
Task 1; if the variable path errors, fall back to `@fontsource/jetbrains-mono`
and `@fontsource/inter` non-variable imports and update `--mono`/`--sans`
font names accordingly.)

- [ ] **Step 3: Commit**

```bash
git add src/layouts/BaseLayout.astro
git commit -m "feat: add BaseLayout with SEO head and no-flash theme script"
```

---

## Task 6: Header, ThemeToggle & Footer components

**Files:**
- Create: `src/components/ThemeToggle.astro`, `src/components/Header.astro`, `src/components/Footer.astro`

- [ ] **Step 1: Create src/components/ThemeToggle.astro**

```astro
<button class="toggle" id="theme-toggle" aria-label="Toggle theme">☾</button>
<style>
  .toggle {
    background: none; border: 1px solid var(--border); color: var(--fg-dim);
    border-radius: 6px; width: 32px; height: 32px; cursor: pointer;
    font-size: 14px; display: grid; place-items: center; transition: all .2s;
  }
  .toggle:hover { border-color: var(--accent); color: var(--accent); }
</style>
<script is:inline>
  (() => {
    const btn = document.getElementById('theme-toggle');
    const sync = () =>
      (btn.textContent =
        document.documentElement.getAttribute('data-theme') === 'light' ? '☀' : '☾');
    sync();
    btn.addEventListener('click', () => {
      const html = document.documentElement;
      const next = html.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
      html.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
      sync();
    });
  })();
</script>
```

- [ ] **Step 2: Create src/components/Header.astro**

```astro
---
import ThemeToggle from './ThemeToggle.astro';
---
<header>
  <div class="wrap nav">
    <a class="brand" href="/"><span class="prompt">~/estudely</span> $ <span class="cursor">▋</span></a>
    <div class="nav-right">
      <nav class="nav-links">
        <a href="/blog">blog</a>
        <a href="/about">about</a>
        <a href="/rss.xml">rss</a>
      </nav>
      <ThemeToggle />
    </div>
  </div>
</header>
<style>
  header { border-bottom: 1px solid var(--border); }
  .nav { display: flex; align-items: center; justify-content: space-between; padding: 22px 24px; }
  .brand { font-family: var(--mono); font-weight: 700; font-size: 15px; color: var(--fg); letter-spacing: -.3px; }
  .brand .prompt { color: var(--accent); }
  .nav-right { display: flex; align-items: center; gap: 22px; }
  .nav-links { display: flex; gap: 20px; }
  .nav-links a { font-family: var(--mono); font-size: 13.5px; color: var(--fg-dim); }
  .nav-links a:hover { color: var(--accent); }
</style>
```

- [ ] **Step 3: Create src/components/Footer.astro**

```astro
---
const year = new Date().getFullYear();
---
<footer>
  <div class="wrap foot">
    <span>© {year} Estudely</span>
    <span>built with astro · <a href="https://github.com/amanverasia">github</a></span>
  </div>
</footer>
<style>
  footer { border-top: 1px solid var(--border); margin-top: 64px; padding: 28px 24px 40px; }
  .foot { display: flex; justify-content: space-between; font-family: var(--mono); font-size: 12.5px; color: var(--fg-faint); flex-wrap: wrap; gap: 12px; padding-left: 0; padding-right: 0; }
  .foot a { color: var(--fg-dim); }
  .foot a:hover { color: var(--accent); }
</style>
```

- [ ] **Step 4: Verify compile**

Run: `npx astro check`
Expected: 0 errors.

- [ ] **Step 5: Commit**

```bash
git add src/components/
git commit -m "feat: add Header, Footer, and ThemeToggle components"
```

---

## Task 7: Reading-time util & PostCard component

**Files:**
- Create: `src/utils/readingTime.ts`, `src/components/PostCard.astro`

- [ ] **Step 1: Create src/utils/readingTime.ts**

```ts
export function readingTime(body: string): string {
  const words = body.trim().split(/\s+/).filter(Boolean).length;
  const minutes = Math.max(1, Math.round(words / 200));
  return `${minutes} min read`;
}
```

- [ ] **Step 2: Create src/components/PostCard.astro**

```astro
---
import type { CollectionEntry } from 'astro:content';
import { readingTime } from '../utils/readingTime';

interface Props { post: CollectionEntry<'blog'> }
const { post } = Astro.props;
const url = `/blog/${post.id}/`;
const dateStr = post.data.date.toISOString().slice(0, 10);
const rt = readingTime(post.body ?? '');
---
<li class="post-item">
  <a href={url}>
    <div class="meta">{dateStr} · {rt}</div>
    <h3>{post.data.title}</h3>
    {post.data.description && <p>{post.data.description}</p>}
    {post.data.tags.length > 0 && (
      <div class="tags">{post.data.tags.map((t) => <span class="tag">#{t}</span>)}</div>
    )}
  </a>
</li>
<style>
  .post-item { padding: 20px 0; border-bottom: 1px solid var(--border); list-style: none; }
  .post-item a { display: block; color: var(--fg); }
  .post-item .meta { font-family: var(--mono); font-size: 12.5px; color: var(--fg-faint); margin-bottom: 6px; }
  .post-item h3 { font-size: 18px; margin: 0 0 6px; font-weight: 600; transition: color .15s; }
  .post-item a:hover h3 { color: var(--accent); }
  .post-item p { margin: 0; color: var(--fg-dim); font-size: 14.5px; }
  .tags { margin-top: 10px; display: flex; gap: 8px; flex-wrap: wrap; }
  .tag { font-family: var(--mono); font-size: 11.5px; color: var(--accent-2); background: var(--bg-soft); border: 1px solid var(--border); padding: 2px 9px; border-radius: 20px; }
</style>
```

Note: `post.id` is Astro's content-layer entry id (the filename without
extension), which matches the existing `slug` frontmatter values, so URLs
stay stable.

- [ ] **Step 3: Verify compile**

Run: `npx astro check`
Expected: 0 errors.

- [ ] **Step 4: Commit**

```bash
git add src/utils/readingTime.ts src/components/PostCard.astro
git commit -m "feat: add reading-time util and PostCard component"
```

---

## Task 8: Home page

**Files:**
- Create: `src/pages/index.astro`

- [ ] **Step 1: Create src/pages/index.astro**

```astro
---
import { getCollection } from 'astro:content';
import BaseLayout from '../layouts/BaseLayout.astro';
import Header from '../components/Header.astro';
import Footer from '../components/Footer.astro';
import PostCard from '../components/PostCard.astro';
import { SOCIALS } from '../consts';

const posts = (await getCollection('blog', ({ data }) => !data.draft)).sort(
  (a, b) => b.data.date.valueOf() - a.data.date.valueOf()
);
const recent = posts.slice(0, 5);
---
<BaseLayout>
  <Header />
  <main class="wrap">
    <section class="hero">
      <div class="greeting">$ whoami</div>
      <h1>Aman Verasia<span class="cursor">_</span></h1>
      <p>Cybersecurity engineer based in Ahmedabad. I break things, secure things,
         and teach the rest on <strong>Estudely</strong>. Notes on infosec, AI,
         and the occasional rabbit hole.</p>
      <div class="socials">
        {SOCIALS.map((s) => <a href={s.href}>{s.label}</a>)}
      </div>
    </section>
    <div class="sec-label">recent posts</div>
    <ul class="posts">{recent.map((post) => <PostCard post={post} />)}</ul>
    <a class="more" href="/blog">cat blog/* →</a>
  </main>
  <Footer />
</BaseLayout>
<style>
  .hero { padding: 60px 0 40px; }
  .greeting { font-family: var(--mono); color: var(--accent); font-size: 14px; margin-bottom: 14px; }
  .hero h1 { font-family: var(--mono); font-size: 30px; line-height: 1.25; margin: 0 0 18px; letter-spacing: -.5px; }
  .hero p { color: var(--fg-dim); font-size: 16px; max-width: 560px; margin: 0 0 24px; }
  .socials { display: flex; gap: 16px; flex-wrap: wrap; font-family: var(--mono); font-size: 13px; }
  .socials a { color: var(--fg-dim); border-bottom: 1px solid transparent; padding-bottom: 2px; }
  .socials a:hover { color: var(--accent); border-color: var(--accent); }
  .sec-label { font-family: var(--mono); font-size: 13px; color: var(--fg-faint); margin: 48px 0 8px; }
  .sec-label::before { content: '// '; color: var(--accent); }
  .posts { list-style: none; margin: 0; padding: 0; }
  .more { font-family: var(--mono); font-size: 13.5px; color: var(--accent); display: inline-block; margin-top: 24px; }
  .more:hover { text-decoration: underline; }
</style>
```

- [ ] **Step 2: Verify build & smoke test**

Run: `npm run build`
Expected: build succeeds, `dist/index.html` produced.

- [ ] **Step 3: Commit**

```bash
git add src/pages/index.astro
git commit -m "feat: add home page with hero and recent posts"
```

---

## Task 9: Blog index & post pages

**Files:**
- Create: `src/pages/blog/index.astro`, `src/pages/blog/[...slug].astro`, `src/layouts/PostLayout.astro`

- [ ] **Step 1: Create src/layouts/PostLayout.astro**

```astro
---
import BaseLayout from './BaseLayout.astro';
import Header from '../components/Header.astro';
import Footer from '../components/Footer.astro';
import { readingTime } from '../utils/readingTime';
import type { CollectionEntry } from 'astro:content';

interface Props { post: CollectionEntry<'blog'> }
const { post } = Astro.props;
const { title, date, description, tags } = post.data;
const dateStr = date.toISOString().slice(0, 10);
const rt = readingTime(post.body ?? '');
const tagStr = tags.map((t) => `#${t}`).join(' ');
---
<BaseLayout title={title} description={description}>
  <Header />
  <main class="wrap">
    <a class="back" href="/blog">cd ..</a>
    <article>
      <div class="post-meta">{dateStr} · {rt}{tagStr && ` · ${tagStr}`}</div>
      <h1>{title}</h1>
      <div class="prose"><slot /></div>
      {tags.length > 0 && (
        <div class="tags">{tags.map((t) => <span class="tag">#{t}</span>)}</div>
      )}
    </article>
  </main>
  <Footer />
</BaseLayout>
<style>
  .back { font-family: var(--mono); font-size: 13px; color: var(--fg-dim); display: inline-block; margin: 36px 0 0; }
  .back:hover { color: var(--accent); }
  article { padding: 20px 0 0; }
  .post-meta { font-family: var(--mono); font-size: 13px; color: var(--fg-faint); margin-bottom: 14px; }
  .post-meta::before { content: '// '; color: var(--accent); }
  article h1 { font-family: var(--mono); font-size: 28px; line-height: 1.3; letter-spacing: -.5px; margin: 0 0 28px; }
  .tags { margin: 40px 0 0; display: flex; gap: 8px; flex-wrap: wrap; }
  .tag { font-family: var(--mono); font-size: 11.5px; color: var(--accent-2); background: var(--bg-soft); border: 1px solid var(--border); padding: 2px 9px; border-radius: 20px; }
</style>
```

- [ ] **Step 2: Create src/pages/blog/[...slug].astro**

```astro
---
import { getCollection, render } from 'astro:content';
import PostLayout from '../../layouts/PostLayout.astro';

export async function getStaticPaths() {
  const posts = await getCollection('blog', ({ data }) => !data.draft);
  return posts.map((post) => ({ params: { slug: post.id }, props: { post } }));
}

const { post } = Astro.props;
const { Content } = await render(post);
---
<PostLayout post={post}>
  <Content />
</PostLayout>
```

- [ ] **Step 3: Create src/pages/blog/index.astro**

```astro
---
import { getCollection } from 'astro:content';
import BaseLayout from '../../layouts/BaseLayout.astro';
import Header from '../../components/Header.astro';
import Footer from '../../components/Footer.astro';
import PostCard from '../../components/PostCard.astro';

const posts = (await getCollection('blog', ({ data }) => !data.draft)).sort(
  (a, b) => b.data.date.valueOf() - a.data.date.valueOf()
);
---
<BaseLayout title="Blog" description="All posts.">
  <Header />
  <main class="wrap">
    <div class="sec-label">all posts</div>
    <ul class="posts">{posts.map((post) => <PostCard post={post} />)}</ul>
  </main>
  <Footer />
</BaseLayout>
<style>
  .sec-label { font-family: var(--mono); font-size: 13px; color: var(--fg-faint); margin: 48px 0 8px; }
  .sec-label::before { content: '// '; color: var(--accent); }
  .posts { list-style: none; margin: 0; padding: 0; }
</style>
```

- [ ] **Step 4: Verify build & smoke test routes**

Run: `npm run build && npm run preview &` then check pages load, then stop preview.

```bash
npm run build
```

Expected: build succeeds; `dist/blog/index.html` and one `dist/blog/<slug>/index.html`
per post are produced (9 post pages). Then:

```bash
(npm run preview &) ; sleep 3
curl -sf http://localhost:4321/blog/ -o /dev/null && echo "blog index OK"
curl -sf http://localhost:4321/blog/what-is-a-rick-roll/ -o /dev/null && echo "post OK"
pkill -f "astro preview"
```

Expected: both echo OK.

- [ ] **Step 5: Commit**

```bash
git add src/layouts/PostLayout.astro src/pages/blog/
git commit -m "feat: add blog index and post pages"
```

---

## Task 10: About page

**Files:**
- Create: `src/pages/about.astro`

- [ ] **Step 1: Create src/pages/about.astro**

Content drawn from existing `content/pages/about-me.md` (bio, quick facts,
education, role, links). Branded Estudely.

```astro
---
import BaseLayout from '../layouts/BaseLayout.astro';
import Header from '../components/Header.astro';
import Footer from '../components/Footer.astro';
import { SOCIALS } from '../consts';
---
<BaseLayout title="About" description="About Aman Verasia and Estudely.">
  <Header />
  <main class="wrap">
    <article class="prose">
      <div class="post-meta">// about</div>
      <h1 class="about-h1">whoami</h1>
      <p>I'm a tech enthusiast based in Ahmedabad, India, with a background in
         mathematics and cybersecurity. I enjoy coding, exploring AI and LLMs,
         and creating educational content. Off-screen: poetry, fiction, and long
         conversations about philosophy and computer science.</p>
      <p>I share what I learn on my YouTube channel, <strong>Estudely</strong> —
         tutorials, explainers, and practical demos for learners at all levels.</p>
      <h2>facts</h2>
      <ul>
        <li>Location: Ahmedabad, India</li>
        <li>Interests: Coding, Cybersecurity, Git, AI, LLMs, Poetry</li>
        <li>Education: MSc Cybersecurity &amp; Digital Forensics · BSc Mathematics</li>
        <li>Role: Senior Software Engineer @ Inventyv Software Services</li>
      </ul>
      <h2>connect</h2>
      <ul class="links">
        {SOCIALS.map((s) => <li><a href={s.href}>{s.label}</a></li>)}
      </ul>
    </article>
  </main>
  <Footer />
</BaseLayout>
<style>
  article { padding: 36px 0 0; }
  .post-meta { font-family: var(--mono); font-size: 13px; color: var(--fg-faint); margin-bottom: 14px; }
  .about-h1 { font-family: var(--mono); font-size: 28px; letter-spacing: -.5px; margin: 0 0 28px; }
  .links { list-style: none; padding-left: 0; font-family: var(--mono); font-size: 14px; }
  .links a { border-bottom: 1px solid var(--border); }
</style>
```

- [ ] **Step 2: Verify build**

Run: `npm run build`
Expected: `dist/about/index.html` produced, 0 errors.

- [ ] **Step 3: Commit**

```bash
git add src/pages/about.astro
git commit -m "feat: add about page"
```

---

## Task 11: RSS feed & 404 page

**Files:**
- Create: `src/pages/rss.xml.js`, `src/pages/404.astro`

- [ ] **Step 1: Create src/pages/rss.xml.js**

```js
import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import { SITE_TITLE, SITE_DESCRIPTION } from '../consts.ts';

export async function GET(context) {
  const posts = (await getCollection('blog', ({ data }) => !data.draft)).sort(
    (a, b) => b.data.date.valueOf() - a.data.date.valueOf()
  );
  return rss({
    title: SITE_TITLE,
    description: SITE_DESCRIPTION,
    site: context.site,
    items: posts.map((post) => ({
      title: post.data.title,
      pubDate: post.data.date,
      description: post.data.description ?? '',
      link: `/blog/${post.id}/`,
    })),
  });
}
```

- [ ] **Step 2: Create src/pages/404.astro**

```astro
---
import BaseLayout from '../layouts/BaseLayout.astro';
import Header from '../components/Header.astro';
import Footer from '../components/Footer.astro';
---
<BaseLayout title="404">
  <Header />
  <main class="wrap notfound">
    <div class="err">$ cd {Astro.url.pathname}</div>
    <p class="msg">bash: no such file or directory</p>
    <h1>404</h1>
    <p>That page doesn't exist. <a href="/">cd ~</a></p>
  </main>
  <Footer />
</BaseLayout>
<style>
  .notfound { padding: 80px 0; font-family: var(--mono); }
  .err { color: var(--accent); }
  .msg { color: var(--fg-dim); }
  .notfound h1 { font-size: 64px; margin: 24px 0 8px; }
  .notfound a { border-bottom: 1px solid var(--border); }
</style>
```

- [ ] **Step 3: Verify build**

Run: `npm run build`
Expected: `dist/rss.xml`, `dist/404.html`, and `dist/sitemap-index.xml`
all produced; 0 errors.

- [ ] **Step 4: Commit**

```bash
git add src/pages/rss.xml.js src/pages/404.astro
git commit -m "feat: add RSS feed and 404 page"
```

---

## Task 12: Public assets (CNAME, favicon, robots)

**Files:**
- Create: `public/CNAME`, `public/favicon.svg`, `public/robots.txt`

- [ ] **Step 1: Create public/CNAME**

```
estudely.com
```

- [ ] **Step 2: Create public/favicon.svg**

A simple terminal-prompt glyph on transparent bg.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect width="32" height="32" rx="6" fill="#0b0e14"/>
  <path d="M7 10l6 6-6 6" fill="none" stroke="#4fd6be" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
  <line x1="16" y1="22" x2="25" y2="22" stroke="#4fd6be" stroke-width="2.5" stroke-linecap="round"/>
</svg>
```

- [ ] **Step 3: Create public/robots.txt**

```
User-agent: *
Allow: /
Sitemap: https://estudely.com/sitemap-index.xml
```

- [ ] **Step 4: Verify build copies assets**

Run: `npm run build`
Expected: `dist/CNAME`, `dist/favicon.svg`, `dist/robots.txt` present.

```bash
ls dist/CNAME dist/favicon.svg dist/robots.txt
```

- [ ] **Step 5: Commit**

```bash
git add public/
git commit -m "feat: add CNAME, favicon, and robots.txt"
```

---

## Task 13: GitHub Pages deploy workflow

**Files:**
- Modify/replace: `.github/workflows/deploy.yml`

- [ ] **Step 1: Replace .github/workflows/deploy.yml**

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-pages-artifact@v3
        with:
          path: ./dist

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

Note: workflow triggers on `main`. Merging `astro-rebuild` into `main` later
will trigger the deploy. The workflow itself can be committed on this branch.

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/deploy.yml
git commit -m "ci: replace deploy workflow with Astro Pages pipeline"
```

---

## Task 14: Remove legacy Python generator & final verification

**Files:**
- Delete: `build.py`, `requirements.txt`, `templates/`, `themes/`, `static/`, old `content/`, root `CNAME`, old `public/` contents, `.preview/`

- [ ] **Step 1: Remove legacy files**

The posts are now in `src/content/blog/`, the about content is in
`src/pages/about.astro`, and CNAME is in `public/CNAME`.

```bash
git rm -r build.py requirements.txt templates themes static content CNAME .preview
git rm -r --ignore-unmatch public/index.html public/blog public/about public/sitemap.xml
```

Note: only remove tracked legacy files. Astro's `public/` (CNAME, favicon,
robots.txt) must remain. If `git rm` reports a path not tracked, skip it.

- [ ] **Step 2: Full clean build & route smoke test**

```bash
rm -rf dist
npm run build
(npm run preview &) ; sleep 3
for path in / /blog/ /about/ /rss.xml /sitemap-index.xml /this-does-not-exist/; do
  code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:4321$path)
  echo "$path -> $code"
done
pkill -f "astro preview"
```

Expected: `/`, `/blog/`, `/about/`, `/rss.xml`, `/sitemap-index.xml` return 200;
the nonexistent path returns 404. `npx astro check` reports 0 errors.

- [ ] **Step 3: Update README**

Replace build/usage instructions to describe the Astro workflow
(`npm install`, `npm run dev`, `npm run build`). Remove references to
`build.py` and the Python toolchain.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "chore: remove legacy Python generator, update README for Astro"
```

---

## Done Criteria

- `npx astro check` → 0 errors.
- `npm run build` → clean build producing home, blog index, 9 posts, about,
  404, rss.xml, sitemap-index.xml.
- Preview smoke test: all main routes 200, unknown route 404.
- Dark/light toggle works and persists with no flash on reload.
- `dist/CNAME` contains `estudely.com`.
- Legacy Python files removed; README updated.
- All work committed on the `astro-rebuild` branch.
