import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

const POST_SLUGS = [
  'choosing-your-ai-co-pilot-a-guide-to-my-favorite-models',
  'for-karnavati-university',
  'for-null-meetup',
  'how-i-hacked-ahem-found-out-about-more-than-10000-ollama-servers',
  'shop',
  'upi-activation-messages-how-they-work-and-security-measures',
  'what-is-a-rick-roll',
  'whats-a-cve-and-why-should-you-care-about-its-potential-disruption',
];

const postRedirects = Object.fromEntries(
  POST_SLUGS.map((slug) => [`/${slug}`, `/blog/${slug}/`]),
);

export default defineConfig({
  site: 'https://estudely.com',
  integrations: [sitemap()],
  redirects: {
    '/about-me': '/about/',
    ...postRedirects,
  },
  markdown: {
    shikiConfig: { theme: 'github-dark', wrap: true },
  },
});
