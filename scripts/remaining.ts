/**
 * List the catalogued problems that still have no solution module.
 *
 *   npx tsx scripts/remaining.ts            # summary
 *   npx tsx scripts/remaining.ts --json     # machine-readable, for batching
 *
 * `tier` is `anchor` for the problems a pattern page walks through in full —
 * those get the deeper treatment — and `core` for everything else.
 */
import { readdirSync, readFileSync, writeFileSync } from 'node:fs'
import path from 'node:path'
import { readCatalogue } from './catalogue.ts'

const ROOT = path.resolve(import.meta.dirname, '..')

export interface Remaining {
  slug: string
  pattern: string
  id: number
  title: string
  difficulty: string
  premium: boolean
  tier: 'anchor' | 'core'
}

export async function remaining(): Promise<Remaining[]> {
  const catalogue = await readCatalogue()
  const problems = JSON.parse(
    readFileSync(path.join(ROOT, 'src/data/generated/problems.json'), 'utf8')
  ) as { slug: string; id: number; title: string; difficulty: string; premium: boolean }[]
  const bySlug = new Map(problems.map((p) => [p.slug, p]))

  const done = new Set(
    readdirSync(path.join(ROOT, 'solutions'))
      .filter((f) => f.endsWith('.py') && !f.startsWith('_'))
      .map((f) => f.replace(/\.py$/, '').replace(/_/g, '-'))
  )

  const seen = new Set<string>()
  const rows: Remaining[] = []
  for (const [pattern, entry] of catalogue.patterns) {
    const anchors = new Set(entry.anchors)
    for (const slug of [...entry.core, ...entry.stretch]) {
      if (done.has(slug) || seen.has(slug)) continue
      const p = bySlug.get(slug)
      if (!p) continue
      seen.add(slug)
      rows.push({
        slug,
        pattern,
        id: p.id,
        title: p.title,
        difficulty: p.difficulty,
        premium: p.premium,
        tier: anchors.has(slug) ? 'anchor' : 'core',
      })
    }
  }
  return rows
}

const rows = await remaining()

if (process.argv.includes('--json')) {
  writeFileSync(path.join(ROOT, 'data', 'remaining.json'), JSON.stringify(rows))
  console.log(`wrote data/remaining.json (${rows.length})`)
} else {
  const byPattern = new Map<string, number>()
  for (const r of rows) byPattern.set(r.pattern, (byPattern.get(r.pattern) ?? 0) + 1)
  console.log(`remaining  ${rows.length}`)
  console.log(`  anchors  ${rows.filter((r) => r.tier === 'anchor').length}`)
  console.log(`  core     ${rows.filter((r) => r.tier === 'core').length}`)
  console.log(`  premium  ${rows.filter((r) => r.premium).length}`)
  for (const [pattern, count] of [...byPattern].sort((a, b) => b[1] - a[1])) {
    console.log(`  ${pattern.padEnd(24)} ${count}`)
  }
}
