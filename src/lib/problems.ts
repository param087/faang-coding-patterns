/**
 * Typed accessors over the generated problem index.
 *
 * `scripts/build-index.ts` writes the JSON; nothing else should reach into it
 * directly, so the compact on-disk shape (window indices, frequency maps)
 * stays an implementation detail.
 */

import companiesRaw from '../data/generated/companies.json'
import logosRaw from '../data/generated/logos.json'
import problemsRaw from '../data/generated/problems.json'
import { PATTERN_BY_ID, PATTERNS } from '../data/taxonomy.ts'

export type Difficulty = 'Easy' | 'Medium' | 'Hard'

export interface Problem {
  slug: string
  id: number
  title: string
  difficulty: Difficulty
  acRate: number
  premium: boolean
  tags: string[]
  pattern: string | null
  curated: boolean
  blind75: boolean
  nc150: boolean
  video?: string
  companies: Record<string, Partial<Record<number, number>>>
  heat: number
}

/**
 * What the explorer island actually needs.
 *
 * `acRate` and `tags` are ~40% of the payload and the table renders neither,
 * so the page ships this narrower shape instead of the full record.
 */
export type ExplorerProblem = Omit<Problem, 'acRate' | 'tags' | 'video'>

export interface Company {
  id: string
  name: string
  core: boolean
  total: number
  recent: number
}

export interface Logo {
  hex: string
  /** Substitute for the dark theme when the brand mark is near-black. */
  hexDark?: string
  path?: string
}

export const WINDOW_LABELS = ['30 days', '3 months', '6 months', 'Older', 'All time'] as const
/** Index into a problem's per-company frequency array. */
export const SIX_MONTHS = 2

export const problems = problemsRaw as Problem[]
export const companies = companiesRaw as Company[]
export const logos = logosRaw as Record<string, Logo>

export const problemBySlug = new Map(problems.map((p) => [p.slug, p]))
export const companyById = new Map(companies.map((c) => [c.id, c]))
export const coreCompanies = companies.filter((c) => c.core)

/** Every problem assigned to a pattern, hottest first. */
export function problemsForPattern(patternId: string): Problem[] {
  return problems
    .filter((p) => p.pattern === patternId)
    .sort((a, b) => b.heat - a.heat || a.id - b.id)
}

/** Companies that ask this problem in the last 6 months, strongest first. */
export function askedBy(problem: Problem): { company: Company; frequency: number }[] {
  const out: { company: Company; frequency: number }[] = []
  for (const [id, windows] of Object.entries(problem.companies)) {
    const frequency = windows[SIX_MONTHS]
    const company = companyById.get(id)
    if (frequency === undefined || !company) continue
    out.push({ company, frequency })
  }
  return out.sort((a, b) => b.frequency - a.frequency)
}

export function logoFor(companyId: string): Logo {
  return logos[companyId] ?? { hex: '888888' }
}

/** Initials for the monogram fallback — two letters, from word starts. */
export function monogram(name: string): string {
  const words = name
    .replace(/[^\w\s]/g, ' ')
    .split(/\s+/)
    .filter(Boolean)
  if (words.length === 0) return '??'
  if (words.length === 1) return (words[0] ?? '').slice(0, 2).toUpperCase()
  return ((words[0]?.[0] ?? '') + (words[1]?.[0] ?? '')).toUpperCase()
}

export interface PatternStats {
  total: number
  easy: number
  medium: number
  hard: number
  /** Highest core-6 six-month frequency in the pattern. */
  heat: number
  topCompanies: { company: Company; count: number }[]
}

/**
 * At the pattern level, *how many* problems a company asks is the useful
 * number. Taking the max frequency instead makes every pattern report the
 * same handful of round percentages, which tells you nothing about whether
 * Google leans on graphs more than Meta does.
 */
export function statsForPattern(patternId: string): PatternStats {
  const list = problemsForPattern(patternId)
  const tally = new Map<string, number>()
  for (const p of list) {
    for (const { company } of askedBy(p)) {
      tally.set(company.id, (tally.get(company.id) ?? 0) + 1)
    }
  }
  const topCompanies = [...tally.entries()]
    .map(([id, count]) => ({ company: companyById.get(id) as Company, count }))
    .filter((x) => x.company?.core)
    .sort((a, b) => b.count - a.count)

  return {
    total: list.length,
    easy: list.filter((p) => p.difficulty === 'Easy').length,
    medium: list.filter((p) => p.difficulty === 'Medium').length,
    hard: list.filter((p) => p.difficulty === 'Hard').length,
    heat: list[0]?.heat ?? 0,
    topCompanies,
  }
}

export { PATTERN_BY_ID, PATTERNS }
