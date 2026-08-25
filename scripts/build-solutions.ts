/**
 * Turn `solutions/*.py` into the data the solution pages render from.
 *
 *   npx tsx scripts/build-solutions.ts
 *
 * A solution is **one file**, not two. Each module carries its own metadata in
 * a `META` dict, its prose in that dict, its code as real functions, and its
 * test cases — so the page and the code cannot drift, and pytest covers
 * everything the site claims.
 *
 * Emits `src/data/generated/solutions.json`.
 */
import { mkdir, readdir, readFile, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { readCatalogue } from './catalogue.ts'

const ROOT = path.resolve(import.meta.dirname, '..')
const SOLUTIONS = path.join(ROOT, 'solutions')
const GEN = path.join(ROOT, 'src', 'data', 'generated')

export interface SolutionRecord {
  slug: string
  /** Which of the 39 patterns owns it. */
  pattern: string
  /** The idea that unlocks it, in one line. */
  insight: string
  time: string
  space: string
  /** Ordered prose sections: heading → markdown body. */
  sections: { heading: string; body: string }[]
  /** Module path, for the Snippet component. */
  module: string
  /** Top-level symbol to show, if the module has more than the solution. */
  symbol?: string
}

/**
 * Pull the `META = {...}` literal out of a Python module.
 *
 * A real Python parser would be better, but the format here is fixed and
 * hand-written, so a targeted extraction is enough — and `check()` in the
 * module plus the Zod-equivalent validation below catches anything malformed.
 */
function parseMeta(source: string, file: string): SolutionRecord {
  const block = /^META\s*=\s*\{([\s\S]*?)^\}/m.exec(source)
  if (!block?.[1]) throw new Error(`${file}: no META block`)
  const body = block[1]

  const scalar = (key: string): string => {
    // Match "key": "value" with either quote style, allowing escaped quotes.
    const re = new RegExp(
      `["']${key}["']\\s*:\\s*(?:"((?:[^"\\\\]|\\\\.)*)"|'((?:[^'\\\\]|\\\\.)*)')`
    )
    const found = re.exec(body)
    const value = found?.[1] ?? found?.[2]
    if (value === undefined) throw new Error(`${file}: META is missing "${key}"`)
    return value.replace(/\\"/g, '"').replace(/\\'/g, "'").replace(/\\n/g, '\n')
  }

  // Sections are a list of (heading, body) tuples using triple-quoted bodies.
  const sections: { heading: string; body: string }[] = []
  const sectionBlock = /["']sections["']\s*:\s*\[([\s\S]*?)\n\s*\],?\s*$/m.exec(body)
  if (sectionBlock?.[1]) {
    const entry = /\(\s*"([^"]+)"\s*,\s*"""([\s\S]*?)"""\s*,?\s*\)/g
    let match: RegExpExecArray | null = entry.exec(sectionBlock[1])
    while (match !== null) {
      sections.push({ heading: match[1] as string, body: (match[2] as string).trim() })
      match = entry.exec(sectionBlock[1])
    }
  }
  if (!sections.length) throw new Error(`${file}: META has no sections`)

  const slug = path.basename(file, '.py').replace(/_/g, '-')
  const symbolMatch = /["']symbol["']\s*:\s*["']([^"']+)["']/.exec(body)

  return {
    slug,
    pattern: scalar('pattern'),
    insight: scalar('insight'),
    time: scalar('time'),
    space: scalar('space'),
    sections,
    module: `solutions/${path.basename(file)}`,
    ...(symbolMatch?.[1] ? { symbol: symbolMatch[1] } : {}),
  }
}

async function main() {
  await mkdir(GEN, { recursive: true })
  await mkdir(SOLUTIONS, { recursive: true })

  const files = (await readdir(SOLUTIONS))
    .filter((f) => f.endsWith('.py') && !f.startsWith('_'))
    .sort()

  const catalogue = await readCatalogue()
  const problems = JSON.parse(await readFile(path.join(GEN, 'problems.json'), 'utf8')) as {
    slug: string
  }[]
  const known = new Set(problems.map((p) => p.slug))

  const records: SolutionRecord[] = []
  const errors: string[] = []

  for (const file of files) {
    const source = await readFile(path.join(SOLUTIONS, file), 'utf8')
    try {
      const record = parseMeta(source, file)
      if (!known.has(record.slug)) {
        errors.push(`${file}: slug "${record.slug}" is not a LeetCode problem`)
        continue
      }
      if (!catalogue.allSlugs.has(record.slug)) {
        errors.push(`${file}: "${record.slug}" is not in CATALOGUE.md`)
        continue
      }
      records.push(record)
    } catch (error) {
      errors.push(`${file}: ${(error as Error).message}`)
    }
  }

  if (errors.length) {
    console.error(`${errors.length} solution errors:`)
    for (const e of errors) console.error(`  ✗ ${e}`)
    process.exit(1)
  }

  await writeFile(path.join(GEN, 'solutions.json'), JSON.stringify(records))

  const byPattern = new Map<string, number>()
  for (const r of records) byPattern.set(r.pattern, (byPattern.get(r.pattern) ?? 0) + 1)

  console.log(`solutions  ${records.length} written of ${catalogue.allSlugs.size} catalogued`)
  for (const [pattern, count] of [...byPattern].sort((a, b) => b[1] - a[1])) {
    console.log(`  ${pattern.padEnd(24)} ${count}`)
  }
}

await main()
