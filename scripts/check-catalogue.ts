/**
 * Validate CATALOGUE.md against the LeetCode snapshot and the taxonomy.
 *
 *   npx tsx scripts/check-catalogue.ts
 *
 * Catches the four ways the catalogue can be wrong:
 *   - a slug that does not exist on LeetCode (typo, or a renamed problem)
 *   - a pattern id that is not in the taxonomy
 *   - an anchor that is not in that pattern's own core or stretch list
 *   - a pattern that is too thin to teach (core < 8, anchors < 2)
 *
 * Also reports duplicates across patterns. A problem living in two patterns
 * is sometimes right — Longest Consecutive Sequence really is both hashing
 * and union-find — so those are warnings, not failures.
 */
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import { PATTERNS } from '../src/data/taxonomy.ts'
import { readCatalogue } from './catalogue.ts'
import type { LeetCodeProblem } from './sources.ts'

const ROOT = path.resolve(import.meta.dirname, '..')
const MIN_CORE = 8
const MIN_ANCHORS = 2

async function main() {
  const leetcode = JSON.parse(
    await readFile(path.join(ROOT, 'data', 'raw', 'leetcode-problems.json'), 'utf8')
  ) as LeetCodeProblem[]
  const known = new Map(leetcode.map((p) => [p.titleSlug, p]))
  const catalogue = await readCatalogue()
  const taxonomyIds = new Set(PATTERNS.map((p) => p.id))

  const errors: string[] = []
  const warnings: string[] = []
  const seen = new Map<string, string[]>()

  for (const id of taxonomyIds) {
    if (!catalogue.patterns.has(id)) errors.push(`pattern "${id}" has no catalogue section`)
  }

  let total = 0
  let premium = 0
  for (const [patternId, entry] of catalogue.patterns) {
    if (!taxonomyIds.has(patternId)) {
      errors.push(`section "${patternId}" is not a pattern in the taxonomy`)
      continue
    }

    const all = [...entry.core, ...entry.stretch]
    for (const slug of all) {
      const problem = known.get(slug)
      if (!problem) {
        errors.push(`${patternId}: slug "${slug}" does not exist on LeetCode`)
        continue
      }
      if (problem.isPaidOnly) premium++
      ;(seen.get(slug) ?? seen.set(slug, []).get(slug))?.push(patternId)
    }
    total += all.length

    const own = new Set(all)
    for (const anchor of entry.anchors) {
      if (!own.has(anchor)) {
        errors.push(`${patternId}: anchor "${anchor}" is not in its own core or stretch list`)
      }
    }
    if (entry.core.length < MIN_CORE) {
      errors.push(`${patternId}: only ${entry.core.length} core problems (need ${MIN_CORE})`)
    }
    if (entry.anchors.length < MIN_ANCHORS) {
      errors.push(`${patternId}: only ${entry.anchors.length} anchors (need ${MIN_ANCHORS})`)
    }
  }

  for (const [slug, patterns] of seen) {
    if (patterns.length > 1) warnings.push(`"${slug}" appears in ${patterns.join(', ')}`)
  }

  const unique = seen.size
  console.log(`sections   ${catalogue.patterns.size}/${taxonomyIds.size}`)
  console.log(`entries    ${total} (${unique} unique problems, ${premium} premium-only)`)
  if (warnings.length) {
    console.log(`\n${warnings.length} problems shared across patterns (allowed):`)
    for (const w of warnings) console.log(`  ${w}`)
  }
  if (errors.length) {
    console.error(`\n${errors.length} errors:`)
    for (const e of errors) console.error(`  ✗ ${e}`)
    process.exit(1)
  }
  console.log('\nCatalogue OK.')
}

await main()
