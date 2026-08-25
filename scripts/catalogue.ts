/**
 * Reader for CATALOGUE.md — the hand-curated half of the problem index.
 *
 * Auto-classification from LeetCode tags is fine for the long tail, but it
 * cannot know that Basic Calculator is String Parsing rather than Stack, or
 * that Design Twitter is Design rather than Heap. So every problem we
 * actually recommend is assigned by hand here, and the catalogue always wins.
 *
 * Format, one section per pattern id:
 *
 *   ## arrays-hashing
 *   - core: two-sum, contains-duplicate, group-anagrams
 *   - stretch: longest-consecutive-sequence
 *   - anchors: two-sum, group-anagrams
 *
 * `core`    the must-do set, in teaching order (>= 8)
 * `stretch` worth doing once core is solid
 * `anchors` the problems that get a full live-solve walkthrough (>= 2, subset of core+stretch)
 */
import { readFile } from 'node:fs/promises'
import path from 'node:path'

// `process.cwd()`, not `import.meta.dirname`: this module is imported both by
// the scripts in this directory and by Astro pages, and Astro's bundler
// rewrites the module location. Both run from the repo root.
const CATALOGUE_PATH = path.resolve(process.cwd(), 'CATALOGUE.md')

export interface PatternEntry {
  core: string[]
  stretch: string[]
  anchors: string[]
}

export interface Catalogue {
  patterns: Map<string, PatternEntry>
  /** slug -> pattern id, for every catalogued problem. */
  patternOf: Map<string, string>
  /** Every slug in the catalogue, core and stretch. */
  allSlugs: Set<string>
}

const EMPTY: Catalogue = { patterns: new Map(), patternOf: new Map(), allSlugs: new Set() }

function parseList(value: string): string[] {
  return value
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean)
}

export function parseCatalogue(text: string): Catalogue {
  const patterns = new Map<string, PatternEntry>()
  const patternOf = new Map<string, string>()
  const allSlugs = new Set<string>()

  let current: string | null = null
  for (const raw of text.split('\n')) {
    const line = raw.trim()
    const heading = /^##\s+([a-z0-9-]+)\s*$/.exec(line)
    if (heading?.[1]) {
      current = heading[1]
      patterns.set(current, { core: [], stretch: [], anchors: [] })
      continue
    }
    if (!current) continue

    const item = /^-\s*(core|stretch|anchors)\s*:\s*(.*)$/.exec(line)
    if (!item?.[1]) continue
    const entry = patterns.get(current)
    if (!entry) continue
    const slugs = parseList(item[2] ?? '')
    entry[item[1] as keyof PatternEntry] = slugs
  }

  for (const [pattern, entry] of patterns) {
    for (const slug of [...entry.core, ...entry.stretch]) {
      // First assignment wins, so a slug listed twice is a catalogue bug we can surface.
      if (!patternOf.has(slug)) patternOf.set(slug, pattern)
      allSlugs.add(slug)
    }
  }
  return { patterns, patternOf, allSlugs }
}

export async function readCatalogue(): Promise<Catalogue> {
  const text = await readFile(CATALOGUE_PATH, 'utf8').catch(() => null)
  if (text === null) return EMPTY
  return parseCatalogue(text)
}
