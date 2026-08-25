/**
 * Join the three snapshots into the artifacts the site reads.
 *
 *   npx tsx scripts/build-index.ts
 *
 * Emits:
 *   src/data/generated/problems.json    every classified problem + core-6 frequencies
 *   src/data/generated/companies.json   the ~659-company directory (id, name, counts)
 *   public/data/companies/<id>.json     per-company slug -> frequency, lazy-loaded
 *
 * Splitting the per-company maps out keeps the explorer's first paint small
 * while still letting you filter by any of the 659 companies.
 */
import { mkdir, readdir, readFile, rm, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { COMBOS, EXCLUDED_TAGS, PATTERNS } from '../src/data/taxonomy.ts'
import { readCatalogue } from './catalogue.ts'
import {
  CORE_COMPANIES,
  type LeetCodeProblem,
  type NeetCodeProblem,
  WINDOWS,
  type Window,
} from './sources.ts'

const ROOT = path.resolve(import.meta.dirname, '..')
const RAW = path.join(ROOT, 'data', 'raw')
const GEN = path.join(ROOT, 'src', 'data', 'generated')
const PUBLIC_COMPANIES = path.join(ROOT, 'public', 'data', 'companies')

/** `Pow(x, n)` has a comma in the title, so index from both ends, never by field count. */
function parseCompanyCsv(text: string): Map<string, number> {
  const out = new Map<string, number>()
  for (const line of text.split('\n').slice(1)) {
    if (!line.trim()) continue
    const parts = line.split(',')
    if (parts.length < 6) continue
    const url = parts[1]
    const freq = parts[parts.length - 1]
    const slug = url?.trim().replace(/\/$/, '').split('/').pop()
    if (!slug) continue
    const value = Number.parseFloat((freq ?? '').replace('%', ''))
    if (!Number.isFinite(value)) continue
    // Keep the strongest signal if a slug somehow appears twice.
    out.set(slug, Math.max(out.get(slug) ?? 0, Math.round(value * 10) / 10))
  }
  return out
}

/** Turn `two-sigma` into `Two Sigma`, with the acronyms that would otherwise look wrong. */
const NAME_OVERRIDES: Record<string, string> = {
  meta: 'Meta',
  tiktok: 'TikTok',
  ibm: 'IBM',
  sap: 'SAP',
  ebay: 'eBay',
  paypal: 'PayPal',
  linkedin: 'LinkedIn',
  github: 'GitHub',
  gitlab: 'GitLab',
  openai: 'OpenAI',
  deepmind: 'DeepMind',
  nvidia: 'NVIDIA',
  amd: 'AMD',
  arm: 'Arm',
  hsbc: 'HSBC',
  jpmorgan: 'JPMorgan',
  'goldman-sachs': 'Goldman Sachs',
  'morgan-stanley': 'Morgan Stanley',
  bny: 'BNY',
  ubs: 'UBS',
  ey: 'EY',
  pwc: 'PwC',
  kpmg: 'KPMG',
  tcs: 'TCS',
  hcl: 'HCL',
  ltimindtree: 'LTIMindtree',
  zoho: 'Zoho',
  byte: 'Byte',
  bytedance: 'ByteDance',
  doordash: 'DoorDash',
  youtube: 'YouTube',
  whatsapp: 'WhatsApp',
  instagram: 'Instagram',
  x: 'X (Twitter)',
  atandt: 'AT&T',
}
function prettyName(id: string): string {
  if (NAME_OVERRIDES[id]) return NAME_OVERRIDES[id] as string
  return id
    .split('-')
    .map((w) => (w.length <= 2 ? w.toUpperCase() : w[0]?.toUpperCase() + w.slice(1)))
    .join(' ')
}

/**
 * Score every pattern against a problem's tags and take the winner.
 *
 * The score is `strongest matched signal + 15% of the rest + combo bonuses`,
 * not a plain sum. A plain sum lets a pile of weakly-related tags out-vote one
 * decisive tag — LRU Cache carries both `linked-list` and `doubly-linked-list`,
 * which together would drown out `design`, the tag that actually names it.
 *
 * Returns null when nothing clears the floor. For a problem tagged only
 * `array`, guessing "Arrays & Hashing" is noise; better to leave it
 * unclassified than to assert something wrong.
 */
function classify(tags: string[]): { pattern: string; confidence: number } | null {
  const tagSet = new Set(tags)
  const bonuses = new Map<string, number>()
  for (const combo of COMBOS) {
    if (combo.all.every((t) => tagSet.has(t))) {
      bonuses.set(combo.pattern, (bonuses.get(combo.pattern) ?? 0) + combo.bonus)
    }
  }

  let best: { pattern: string; score: number } | null = null
  for (const p of PATTERNS) {
    const matched: number[] = []
    for (const [tag, weight] of Object.entries(p.signals)) {
      if (tagSet.has(tag)) matched.push(weight)
    }
    const bonus = bonuses.get(p.id) ?? 0
    if (!matched.length && !bonus) continue
    const strongest = matched.length ? Math.max(...matched) : 0
    const rest = matched.reduce((a, b) => a + b, 0) - strongest
    const score = strongest + rest * 0.15 + bonus
    if (!best || score > best.score) best = { pattern: p.id, score }
  }
  if (!best || best.score < 10) return null
  return { pattern: best.pattern, confidence: Math.round(best.score) }
}

interface ProblemRecord {
  slug: string
  id: number
  title: string
  difficulty: 'Easy' | 'Medium' | 'Hard'
  acRate: number
  premium: boolean
  tags: string[]
  pattern: string | null
  /** true when a human put it there via CATALOGUE.md, false when auto-classified. */
  curated: boolean
  blind75: boolean
  nc150: boolean
  /** NeetCode solution video ID, when one exists. */
  video?: string
  /** Core-6 frequencies only, keyed by company id then window index. */
  companies: Record<string, Partial<Record<number, number>>>
  /** Highest core-6 frequency in the 6-month window — the default sort key. */
  heat: number
}

async function main() {
  const leetcode = JSON.parse(
    await readFile(path.join(RAW, 'leetcode-problems.json'), 'utf8')
  ) as LeetCodeProblem[]
  const neetcode = JSON.parse(
    await readFile(path.join(RAW, 'neetcode.json'), 'utf8')
  ) as NeetCodeProblem[]

  const ncBySlug = new Map(neetcode.map((n) => [n.link.replace(/\/$/, ''), n]))

  // --- company frequencies -------------------------------------------------
  const companyDirs = (await readdir(path.join(RAW, 'companies'), { withFileTypes: true }))
    .filter((d) => d.isDirectory())
    .map((d) => d.name)
    .sort()

  /** companyId -> window -> (slug -> frequency) */
  const freq = new Map<string, Map<Window, Map<string, number>>>()
  for (const dir of companyDirs) {
    const perWindow = new Map<Window, Map<string, number>>()
    for (const window of WINDOWS) {
      const file = path.join(RAW, 'companies', dir, `${window}.csv`)
      const text = await readFile(file, 'utf8').catch(() => null)
      if (text) perWindow.set(window, parseCompanyCsv(text))
    }
    freq.set(dir, perWindow)
  }

  const coreIds = new Set<string>(CORE_COMPANIES.map((c) => c.dir))
  const catalogue = await readCatalogue()

  // --- problems ------------------------------------------------------------
  const problems: ProblemRecord[] = []
  for (const p of leetcode) {
    const tags = p.topicTags.map((t) => t.slug)
    if (tags.some((t) => EXCLUDED_TAGS.has(t))) continue // SQL / shell aren't coding-round problems

    const nc = ncBySlug.get(p.titleSlug)
    const curatedPattern = catalogue.patternOf.get(p.titleSlug) ?? null
    const auto = classify(tags)

    const companies: ProblemRecord['companies'] = {}
    let heat = 0
    for (const id of coreIds) {
      const perWindow = freq.get(id)
      if (!perWindow) continue
      const entry: Partial<Record<number, number>> = {}
      for (const [i, window] of WINDOWS.entries()) {
        const f = perWindow.get(window)?.get(p.titleSlug)
        if (f !== undefined) entry[i] = f
      }
      if (Object.keys(entry).length) {
        companies[id] = entry
        const sixMonth = entry[WINDOWS.indexOf('six-months')] ?? 0
        heat = Math.max(heat, sixMonth)
      }
    }

    problems.push({
      slug: p.titleSlug,
      id: Number.parseInt(p.questionFrontendId, 10),
      title: p.title,
      difficulty: p.difficulty,
      acRate: Math.round(p.acRate * 10) / 10,
      premium: p.isPaidOnly,
      tags,
      pattern: curatedPattern ?? auto?.pattern ?? null,
      curated: curatedPattern !== null,
      blind75: nc?.blind75 === true,
      nc150: nc?.neetcode150 === true,
      ...(nc?.video ? { video: nc.video } : {}),
      companies,
      heat,
    })
  }
  problems.sort((a, b) => a.id - b.id)

  // --- company directory ---------------------------------------------------
  const directory = companyDirs.map((id) => {
    const perWindow = freq.get(id)
    return {
      id,
      name: prettyName(id),
      core: coreIds.has(id),
      total: perWindow?.get('all')?.size ?? 0,
      recent: perWindow?.get('six-months')?.size ?? 0,
    }
  })
  directory.sort((a, b) => b.recent - a.recent || a.name.localeCompare(b.name))

  await mkdir(GEN, { recursive: true })
  await rm(PUBLIC_COMPANIES, { recursive: true, force: true })
  await mkdir(PUBLIC_COMPANIES, { recursive: true })

  await writeFile(path.join(GEN, 'problems.json'), JSON.stringify(problems))
  await writeFile(path.join(GEN, 'companies.json'), JSON.stringify(directory, null, 2))

  // Per-company maps, lazy-loaded by the explorer. Windows become arrays so
  // the payload stays terse: [thirtyDays, threeMonths, sixMonths, older, all].
  for (const [id, perWindow] of freq) {
    const merged: Record<string, (number | null)[]> = {}
    for (const [i, window] of WINDOWS.entries()) {
      for (const [slug, f] of perWindow.get(window) ?? []) {
        merged[slug] ??= [null, null, null, null, null]
        ;(merged[slug] as (number | null)[])[i] = f
      }
    }
    await writeFile(path.join(PUBLIC_COMPANIES, `${id}.json`), JSON.stringify(merged))
  }

  // --- report --------------------------------------------------------------
  const classified = problems.filter((p) => p.pattern).length
  const curated = problems.filter((p) => p.curated).length
  console.log(
    `problems     ${problems.length} (${leetcode.length - problems.length} SQL/shell dropped)`
  )
  console.log(`classified   ${classified} (${curated} hand-curated, ${classified - curated} auto)`)
  console.log(`unclassified ${problems.length - classified}`)
  console.log(`companies    ${directory.length}`)
  for (const c of CORE_COMPANIES) {
    const n = problems.filter((p) => p.companies[c.dir]).length
    console.log(`  ${c.name.padEnd(10)} ${n} tagged problems`)
  }
}

await main()
