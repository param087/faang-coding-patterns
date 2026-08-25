/**
 * Sampled reachability check for the outbound links.
 *
 *   npx tsx scripts/check-links.ts --sample 60
 *
 * The site links to thousands of LeetCode problems and hundreds of NeetCode
 * videos; checking all of them on every run would take minutes and get us
 * rate-limited. A random sample per run catches slug rot — problems do get
 * renamed — without the cost. Catalogued problems are sampled preferentially
 * because those are the links the site actually recommends.
 *
 * Network failure is reported but does not fail the gate: a flaky connection
 * should not block a docs deploy. A 404 does fail.
 */
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import { readCatalogue } from './catalogue.ts'

const ROOT = path.resolve(import.meta.dirname, '..')
const sampleArg = process.argv.indexOf('--sample')
const SAMPLE = sampleArg > -1 ? Number(process.argv[sampleArg + 1]) : 40

interface Row {
  slug: string
  video?: string
}

/** Deterministic shuffle so a failing run can be reproduced from the seed. */
function shuffle<T>(items: T[], seed: number): T[] {
  const out = [...items]
  let state = seed
  for (let i = out.length - 1; i > 0; i--) {
    state = (state * 1103515245 + 12345) % 2 ** 31
    const j = state % (i + 1)
    ;[out[i], out[j]] = [out[j] as T, out[i] as T]
  }
  return out
}

async function head(url: string): Promise<number | 'network'> {
  try {
    const res = await fetch(url, {
      method: 'GET',
      redirect: 'follow',
      headers: { 'User-Agent': 'Mozilla/5.0 faang-coding-patterns link check' },
    })
    return res.status
  } catch {
    return 'network'
  }
}

async function main() {
  const problems = JSON.parse(
    await readFile(path.join(ROOT, 'src', 'data', 'generated', 'problems.json'), 'utf8')
  ) as (Row & { curated: boolean })[]
  const catalogue = await readCatalogue()

  const curated = problems.filter((p) => catalogue.allSlugs.has(p.slug))
  const seed = Number(process.env.LINK_SEED ?? 20260825)
  const picks = shuffle(curated, seed).slice(0, SAMPLE)

  const failures: string[] = []
  let networkErrors = 0
  let checked = 0

  for (const p of picks) {
    const urls = [`https://leetcode.com/problems/${p.slug}/`]
    if (p.video) urls.push(`https://www.youtube.com/watch?v=${p.video}`)
    for (const url of urls) {
      const status = await head(url)
      checked++
      if (status === 'network') networkErrors++
      else if (status === 404 || status === 410) failures.push(`${status} ${url}`)
      await new Promise((r) => setTimeout(r, 120))
    }
  }

  console.log(`checked   ${checked} links (seed ${seed}, sample ${SAMPLE} problems)`)
  if (networkErrors) console.log(`network   ${networkErrors} unreachable — not treated as failures`)
  if (failures.length) {
    console.error(`\n${failures.length} dead links:`)
    for (const f of failures) console.error(`  ✗ ${f}`)
    process.exit(1)
  }
  console.log('Links OK.')
}

await main()
