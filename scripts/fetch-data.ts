/**
 * Snapshot the three upstream sources into `data/raw/`.
 *
 *   npx tsx scripts/fetch-data.ts            # skip anything already on disk
 *   npx tsx scripts/fetch-data.ts --refresh  # re-pull everything
 *
 * `data/raw/` is committed on purpose: the site must build offline, and a
 * frozen snapshot means a rebuild never silently changes what problems the
 * pages recommend.
 */

import { existsSync } from 'node:fs'
import { mkdir, readdir, readFile, writeFile } from 'node:fs/promises'
import path from 'node:path'
import {
  COMPANY_REPO,
  COMPANY_REPO_TREE,
  LEETCODE_GRAPHQL,
  type LeetCodeProblem,
  NEETCODE_JSON,
  WINDOWS,
} from './sources.ts'

const ROOT = path.resolve(import.meta.dirname, '..')
const RAW = path.join(ROOT, 'data', 'raw')
const COMPANIES_DIR = path.join(RAW, 'companies')
const REFRESH = process.argv.includes('--refresh')

const UA =
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) faang-coding-patterns/0.1 (build-time snapshot)'
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms))

/** fetch with retry — upstream throttles, and a half-written snapshot is worse than a slow one. */
async function get(url: string, init?: RequestInit, attempts = 4): Promise<Response> {
  let lastErr: unknown
  for (let i = 0; i < attempts; i++) {
    try {
      const res = await fetch(url, { ...init, headers: { 'User-Agent': UA, ...init?.headers } })
      if (res.ok) return res
      if (res.status === 404) return res // a genuine "not there", not worth retrying
      lastErr = new Error(`${res.status} ${res.statusText} for ${url}`)
    } catch (err) {
      lastErr = err
    }
    await sleep(500 * 2 ** i)
  }
  throw lastErr
}

/** All ~4,000 LeetCode problems, 100 at a time. */
async function fetchLeetCode(): Promise<void> {
  const out = path.join(RAW, 'leetcode-problems.json')
  if (existsSync(out) && !REFRESH) return void console.log('  leetcode  cached')

  const query = `query ($limit: Int!, $skip: Int!) {
    questionList(categorySlug: "", limit: $limit, skip: $skip, filters: {}) {
      total: totalNum
      data { questionFrontendId title titleSlug difficulty acRate isPaidOnly topicTags { name slug } }
    }
  }`

  const all: LeetCodeProblem[] = []
  let total = Infinity
  for (let skip = 0; skip < total; skip += 100) {
    const res = await get(LEETCODE_GRAPHQL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, variables: { limit: 100, skip } }),
    })
    const json = (await res.json()) as {
      data: { questionList: { total: number; data: LeetCodeProblem[] } }
    }
    const page = json.data.questionList
    total = page.total
    all.push(...page.data)
    process.stdout.write(`\r  leetcode  ${all.length}/${total}`)
    await sleep(250) // be a polite client
  }
  await writeFile(out, JSON.stringify(all))
  console.log(`\r  leetcode  ${all.length} problems`)
}

/** NeetCode's curated 450 with pattern, list flags and solution-video IDs. */
async function fetchNeetCode(): Promise<void> {
  const out = path.join(RAW, 'neetcode.json')
  if (existsSync(out) && !REFRESH) return void console.log('  neetcode  cached')
  const res = await get(NEETCODE_JSON)
  const text = await res.text()
  await writeFile(out, text)
  console.log(`  neetcode  ${(JSON.parse(text) as unknown[]).length} problems`)
}

/**
 * Every company folder, every time window.
 *
 * One tree call lists the whole repo, so we discover the ~600 company
 * directories rather than hard-coding them — new companies appear upstream
 * over time and we want them in the explorer for free.
 */
async function fetchCompanies(): Promise<void> {
  await mkdir(COMPANIES_DIR, { recursive: true })
  const existing = new Set(await readdir(COMPANIES_DIR).catch(() => []))

  const res = await get(`${COMPANY_REPO_TREE}?recursive=1`)
  const tree = (await res.json()) as { tree: { path: string; type: string }[] }
  const wanted = new Map<string, Set<string>>()
  for (const node of tree.tree) {
    if (node.type !== 'blob' || !node.path.endsWith('.csv')) continue
    const [dir, file] = node.path.split('/')
    if (!dir || !file) continue
    const window = file.replace(/\.csv$/, '')
    if (!(WINDOWS as readonly string[]).includes(window)) continue
    if (!wanted.has(dir)) wanted.set(dir, new Set())
    wanted.get(dir)?.add(window)
  }
  console.log(`  companies ${wanted.size} directories upstream`)

  let done = 0
  const dirs = [...wanted.entries()].sort(([a], [b]) => a.localeCompare(b))
  // Modest concurrency: fast enough for ~2,500 small files, gentle on raw.githubusercontent.
  const CONCURRENCY = 8
  for (let i = 0; i < dirs.length; i += CONCURRENCY) {
    await Promise.all(
      dirs.slice(i, i + CONCURRENCY).map(async ([dir, windows]) => {
        const target = path.join(COMPANIES_DIR, dir)
        if (existing.has(dir) && !REFRESH) return void done++
        await mkdir(target, { recursive: true })
        for (const window of windows) {
          const r = await get(`${COMPANY_REPO}/${dir}/${window}.csv`)
          if (!r.ok) continue
          await writeFile(path.join(target, `${window}.csv`), await r.text())
        }
        done++
      })
    )
    process.stdout.write(`\r  companies ${done}/${dirs.length}`)
  }
  console.log(`\r  companies ${done} fetched`)
}

async function main() {
  await mkdir(RAW, { recursive: true })
  console.log(REFRESH ? 'Refreshing snapshot...' : 'Fetching snapshot (cached files kept)...')
  await fetchLeetCode()
  await fetchNeetCode()
  await fetchCompanies()

  // Stamp the snapshot so the UI can say how stale it is.
  const lc = JSON.parse(
    await readFile(path.join(RAW, 'leetcode-problems.json'), 'utf8')
  ) as unknown[]
  await writeFile(
    path.join(RAW, 'snapshot.json'),
    JSON.stringify(
      {
        fetchedAt: new Date().toISOString().slice(0, 10),
        leetcodeProblems: lc.length,
        companies: (await readdir(COMPANIES_DIR)).length,
      },
      null,
      2
    )
  )
  console.log('Done.')
}

await main()
