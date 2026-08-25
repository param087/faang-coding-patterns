/**
 * Base-aware URLs.
 *
 * The site is served from a repo subpath on GitHub Pages, so a bare `/foo/`
 * href works in `astro dev` and 404s in production. Everything internal goes
 * through `href()`.
 */
const BASE = import.meta.env.BASE_URL.replace(/\/$/, '')

export function href(path: string): string {
  const clean = path.startsWith('/') ? path : `/${path}`
  const withSlash = clean.endsWith('/') || clean.includes('.') ? clean : `${clean}/`
  return `${BASE}${withSlash}`
}

export const routes = {
  home: () => href('/'),
  patterns: () => href('/patterns/'),
  pattern: (id: string) => href(`/patterns/${id}/`),
  problems: () => href('/problems/'),
  problem: (slug: string) => href(`/problems/${slug}/`),
  explorer: () => href('/explorer/'),
  companies: () => href('/companies/'),
  company: (id: string) => href(`/companies/${id}/`),
  plans: () => href('/plans/'),
  plan: (id: string) => href(`/plans/${id}/`),
  guide: (slug: string) => href(`/guide/${slug}/`),
  styleguide: () => href('/styleguide/'),
}

export const external = {
  leetcode: (slug: string) => `https://leetcode.com/problems/${slug}/`,
  youtube: (id: string) => `https://www.youtube.com/watch?v=${id}`,
}
