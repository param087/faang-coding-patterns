// @ts-check

import mdx from '@astrojs/mdx'
import react from '@astrojs/react'
import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'astro/config'

// Published to GitHub Pages under a repo subpath, so `base` matters: every
// internal href must go through `src/lib/paths.ts#href()` rather than a bare
// absolute path, or it 404s in production while working fine in `astro dev`.
export default defineConfig({
  site: 'https://param087.github.io',
  base: '/faang-coding-patterns',
  trailingSlash: 'always',
  integrations: [mdx(), react()],
  vite: { plugins: [tailwindcss()] },
  markdown: {
    shikiConfig: {
      themes: { light: 'github-light', dark: 'github-dark-default' },
      wrap: false,
    },
  },
  build: { format: 'directory' },
})
