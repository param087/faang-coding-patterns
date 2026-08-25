/**
 * The three upstream data sources, and the shapes they hand back.
 *
 * All three were verified reachable without credentials. None of them are
 * hit at runtime: `fetch-data.ts` snapshots them into `data/raw/`, which is
 * committed, so the site builds offline and reproducibly.
 */

export const LEETCODE_GRAPHQL = 'https://leetcode.com/graphql'

/** NeetCode's own problem metadata: pattern, list membership, solution video. */
export const NEETCODE_JSON =
  'https://raw.githubusercontent.com/neetcode-gh/leetcode/main/.problemSiteData.json'

/** Community snapshot of LeetCode Premium company tags (12 Jul 2026). */
export const COMPANY_REPO =
  'https://raw.githubusercontent.com/snehasishroy/leetcode-companywise-interview-questions/master'
export const COMPANY_REPO_TREE =
  'https://api.github.com/repos/snehasishroy/leetcode-companywise-interview-questions/git/trees/master'

/** The date the company-tag snapshot upstream was taken. Rendered in the UI. */
export const COMPANY_SNAPSHOT_DATE = '2026-07-12'

/**
 * Time windows the company CSVs are bucketed into, narrowest first.
 * `six-months` is the default everywhere: wide enough to be stable, recent
 * enough to reflect the current question bank.
 */
export const WINDOWS = [
  'thirty-days',
  'three-months',
  'six-months',
  'more-than-six-months',
  'all',
] as const
export type Window = (typeof WINDOWS)[number]
export const DEFAULT_WINDOW: Window = 'six-months'

/**
 * The six companies that get logo badge columns and a playbook page.
 * `dir` is the folder name upstream — note Meta is `meta`, not `facebook`.
 */
export const CORE_COMPANIES = [
  { id: 'google', dir: 'google', name: 'Google', domain: 'google.com', icon: 'google' },
  { id: 'meta', dir: 'meta', name: 'Meta', domain: 'meta.com', icon: 'meta' },
  { id: 'amazon', dir: 'amazon', name: 'Amazon', domain: 'amazon.com', icon: 'amazon' },
  {
    id: 'microsoft',
    dir: 'microsoft',
    name: 'Microsoft',
    domain: 'microsoft.com',
    icon: 'microsoft',
  },
  { id: 'apple', dir: 'apple', name: 'Apple', domain: 'apple.com', icon: 'apple' },
  { id: 'netflix', dir: 'netflix', name: 'Netflix', domain: 'netflix.com', icon: 'netflix' },
] as const
export type CoreCompanyId = (typeof CORE_COMPANIES)[number]['id']

export interface LeetCodeProblem {
  questionFrontendId: string
  title: string
  titleSlug: string
  difficulty: 'Easy' | 'Medium' | 'Hard'
  acRate: number
  isPaidOnly: boolean
  topicTags: { name: string; slug: string }[]
}

export interface NeetCodeProblem {
  problem: string
  /** NeetCode's own 19-bucket taxonomy. We map it into our 39. */
  pattern: string
  /** LeetCode slug with a trailing slash, e.g. `contains-duplicate/`. */
  link: string
  /** YouTube video ID of NeetCode's walkthrough. */
  video?: string
  difficulty: string
  blind75?: boolean
  neetcode150?: boolean
  premium?: boolean
}

/** One row of a company CSV: `ID,URL,Title,Difficulty,Acceptance %,Frequency %`. */
export interface CompanyRow {
  slug: string
  frequency: number
}
