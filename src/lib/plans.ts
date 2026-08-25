/**
 * The three study tracks.
 *
 * Each is a sequence of weeks naming patterns, generated against the catalogue
 * so the problem counts are real rather than aspirational. The difference
 * between them is coverage, not pace: the sprint drops the long tail, the
 * thorough track keeps everything and revisits.
 */
import { PATTERNS } from '../data/taxonomy.ts'

export interface Week {
  n: number
  focus: string
  patterns: string[]
  /** What this week is actually for, beyond the pattern list. */
  note: string
}

export interface Plan {
  id: string
  name: string
  weeks: number
  /** Who it's for, in one line. */
  audience: string
  /** Realistic daily commitment. */
  commitment: string
  /** Which lists to draw from within each pattern. */
  scope: 'core' | 'core+stretch'
  schedule: Week[]
}

export const PLANS: Plan[] = [
  {
    id: 'sprint',
    name: '4-week sprint',
    weeks: 4,
    audience: 'Onsite is booked and close. You have interviewed before.',
    commitment: '2–3 hours a day, core lists only',
    scope: 'core',
    schedule: [
      {
        n: 1,
        focus: 'The linear scans',
        patterns: ['arrays-hashing', 'two-pointers', 'sliding-window', 'prefix-sums', 'stack'],
        note: 'These carry the most weight per hour. If a round opens easy, it opens here.',
      },
      {
        n: 2,
        focus: 'Search, trees and heaps',
        patterns: [
          'binary-search',
          'binary-search-answer',
          'binary-trees',
          'heaps',
          'linked-lists',
        ],
        note: 'Binary search on the answer is the highest-leverage thing on this page — most candidates never reach for it.',
      },
      {
        n: 3,
        focus: 'Graphs and DP',
        patterns: [
          'graph-traversal',
          'topological-sort',
          'union-find',
          'dp-1d',
          'dp-grid-knapsack',
        ],
        note: 'The densest week. Graphs and DP together are close to half of Medium/Hard rounds.',
      },
      {
        n: 4,
        focus: 'Design, greedy, and mocks',
        patterns: ['design', 'greedy', 'intervals', 'backtracking'],
        note: 'Half the week on mocks under a real clock. Untimed practice does not transfer.',
      },
    ],
  },
  {
    id: 'standard',
    name: '8-week standard',
    weeks: 8,
    audience: 'The default. Interviews roughly two months out.',
    commitment: '2 hours a day, core plus some stretch',
    scope: 'core+stretch',
    schedule: [
      {
        n: 1,
        focus: 'Arrays, hashing, two pointers',
        patterns: ['arrays-hashing', 'two-pointers', 'prefix-sums'],
        note: 'Build the habit of stating complexity out loud before writing code.',
      },
      {
        n: 2,
        focus: 'Windows, stacks and strings',
        patterns: ['sliding-window', 'stack', 'monotonic-stack', 'string-manipulation'],
        note: 'The at-most-K trick and the monotonic stack are the two techniques to get automatic.',
      },
      {
        n: 3,
        focus: 'Sorting, intervals, matrices',
        patterns: ['sorting', 'intervals', 'matrix'],
        note: 'Mostly about choosing the sort key and not fumbling the sweep.',
      },
      {
        n: 4,
        focus: 'Binary search, both kinds',
        patterns: ['binary-search', 'binary-search-answer', 'divide-and-conquer'],
        note: 'Write the bounds template once, from memory, and stop re-deriving it.',
      },
      {
        n: 5,
        focus: 'Linked structures and trees',
        patterns: ['linked-lists', 'binary-trees', 'binary-search-trees', 'tries', 'heaps'],
        note: 'For every tree problem ask "what does a node return to its parent" before writing anything.',
      },
      {
        n: 6,
        focus: 'Graphs, all of them',
        patterns: ['graph-traversal', 'topological-sort', 'union-find', 'shortest-paths'],
        note: 'The single densest category at SDE-2. Do not shortcut this week.',
      },
      {
        n: 7,
        focus: 'Dynamic programming',
        patterns: ['dp-1d', 'dp-grid-knapsack', 'dp-strings', 'greedy', 'backtracking'],
        note: 'State first, recurrence second, table third. Most DP failures are state failures.',
      },
      {
        n: 8,
        focus: 'Design, the long tail, and mocks',
        patterns: ['design', 'ood', 'bit-manipulation', 'math-geometry', 'ordered-set'],
        note: 'Design is where SDE-2 rounds are decided and where lists leave you exposed. Then mock daily.',
      },
    ],
  },
  {
    id: 'thorough',
    name: '12-week thorough',
    weeks: 12,
    audience: 'Time to do it properly, or coming back after a long gap.',
    commitment: '2 hours a day, everything, with spaced review',
    scope: 'core+stretch',
    schedule: [
      {
        n: 1,
        focus: 'Arrays and hashing',
        patterns: ['arrays-hashing', 'prefix-sums'],
        note: 'Slow and complete. Every core problem, written out, not read.',
      },
      {
        n: 2,
        focus: 'Two pointers and windows',
        patterns: ['two-pointers', 'sliding-window'],
        note: 'Revisit week 1 on the last day — first spaced-repetition checkpoint.',
      },
      {
        n: 3,
        focus: 'Stacks',
        patterns: ['stack', 'monotonic-stack'],
        note: 'Largest Rectangle until the width arithmetic is automatic.',
      },
      {
        n: 4,
        focus: 'Sorting, intervals, matrices',
        patterns: ['sorting', 'intervals', 'matrix'],
        note: 'Sweep line properly, not just merge intervals.',
      },
      {
        n: 5,
        focus: 'Strings',
        patterns: ['string-manipulation', 'string-algorithms'],
        note: 'KMP and rolling hash. Rare, but nothing else saves you when they appear.',
      },
      {
        n: 6,
        focus: 'Binary search',
        patterns: ['binary-search', 'binary-search-answer'],
        note: 'Review weeks 1–3.',
      },
      {
        n: 7,
        focus: 'Linked lists and trees',
        patterns: ['linked-lists', 'binary-trees', 'binary-search-trees'],
        note: 'Serialize/deserialize and LCA from memory.',
      },
      {
        n: 8,
        focus: 'Tries, heaps, ordered sets',
        patterns: ['tries', 'heaps', 'ordered-set'],
        note: 'The sortedcontainers question matters — know your platform.',
      },
      {
        n: 9,
        focus: 'Graph traversal and ordering',
        patterns: ['graph-traversal', 'topological-sort', 'union-find'],
        note: 'Review weeks 4–6.',
      },
      {
        n: 10,
        focus: 'Weighted graphs',
        patterns: ['shortest-paths', 'minimum-spanning-tree', 'advanced-graphs'],
        note: 'Dijkstra from memory, including the lazy-deletion heap detail.',
      },
      {
        n: 11,
        focus: 'Dynamic programming and recursion',
        patterns: [
          'dp-1d',
          'dp-grid-knapsack',
          'dp-strings',
          'dp-advanced',
          'backtracking',
          'divide-and-conquer',
          'greedy',
        ],
        note: 'The heaviest week. Bitmask DP included.',
      },
      {
        n: 12,
        focus: 'Design, systems and mocks',
        patterns: [
          'design',
          'ood',
          'concurrency',
          'segment-tree',
          'randomized',
          'bit-manipulation',
          'math-geometry',
        ],
        note: 'Everything the lists skip, then mocks daily under a hard clock.',
      },
    ],
  },
]

export const PLAN_BY_ID = new Map(PLANS.map((p) => [p.id, p]))

/** Patterns a plan never covers — stated plainly rather than quietly dropped. */
export function omittedBy(plan: Plan): string[] {
  const covered = new Set(plan.schedule.flatMap((w) => w.patterns))
  return PATTERNS.filter((p) => !covered.has(p.id)).map((p) => p.id)
}
