/**
 * Content collections, schema-gated.
 *
 * The Zod schemas here replace the bespoke completeness checker the sibling
 * HLD/LLD handbook uses: a pattern page that forgets its recognition cues, or
 * names an anchor that isn't in the catalogue, fails `astro build` rather
 * than shipping a half-written page.
 */
import { defineCollection, z } from 'astro:content'
import { glob } from 'astro/loaders'
import { PATTERNS } from './data/taxonomy.ts'

const patternIds = PATTERNS.map((p) => p.id) as [string, ...string[]]

const patterns = defineCollection({
  loader: glob({ base: './src/content/patterns', pattern: '**/*.mdx' }),
  schema: z.object({
    /** Must match a taxonomy id; the file name must match too. */
    id: z.enum(patternIds),
    title: z.string(),
    /** The 10-second recognition cues. At least three, or the page isn't useful. */
    recognition: z.array(z.string()).min(3),
    /** Complexity you quote in the round for the canonical solution. */
    complexity: z.string(),
    /** Repo-relative path to the tested template module. */
    template: z.string().startsWith('code/'),
    /** Problems that get a full live-solve walkthrough on this page. */
    anchors: z.array(z.string()).min(2),
    /** Adjacent patterns, by id. */
    related: z.array(z.enum(patternIds)).default([]),
  }),
})

const solutions = defineCollection({
  loader: glob({ base: './src/content/solutions', pattern: '**/*.mdx' }),
  schema: z.object({
    /** LeetCode titleSlug. Must exist in the problem index. */
    slug: z.string(),
    title: z.string(),
    /** Owning pattern id. */
    pattern: z.enum(patternIds),
    /** Repo-relative path to the tested solution module. */
    solution: z.string().startsWith('solutions/'),
    time: z.string(),
    space: z.string(),
    /** One line on the idea that unlocks it — shown in listings. */
    insight: z.string(),
  }),
})

const guide = defineCollection({
  loader: glob({ base: './src/content/guide', pattern: '**/*.mdx' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    /** Nav ordering within the guide section. */
    order: z.number(),
  }),
})

export const collections = { patterns, solutions, guide }
