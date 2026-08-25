/**
 * The complexity ramp — the site's organising idea.
 *
 * An SDE-2 is expected to read a problem's constraints and know the shape of
 * the answer before reading the problem itself. `n <= 20` means "exponential
 * is fine, find the bitmask". `n <= 10^5` means "O(n log n) or better, stop
 * looking for the clever quadratic". This module encodes that reflex, and its
 * class ids double as the site's colour tokens.
 */

export type ComplexityId = 'o1' | 'on' | 'onlogn' | 'on2' | 'oexp'

export interface ComplexityClass {
  id: ComplexityId
  /** Rendered with proper notation, e.g. `O(n log n)`. */
  label: string
  /** What it costs, in one phrase. */
  gloss: string
  /** Operations for a given n. Used to decide feasibility. */
  ops: (n: number) => number
}

/**
 * ~10^8 simple operations is the usual one-second budget on an online judge,
 * and a reasonable stand-in for "will this pass" in an interview.
 */
export const OPS_BUDGET = 1e8

export const COMPLEXITY_CLASSES: ComplexityClass[] = [
  {
    id: 'o1',
    label: 'O(log n)',
    gloss: 'Constant or logarithmic — n barely matters',
    ops: (n) => Math.log2(Math.max(n, 2)),
  },
  { id: 'on', label: 'O(n)', gloss: 'One pass', ops: (n) => n },
  {
    id: 'onlogn',
    label: 'O(n log n)',
    gloss: 'Sort, or a heap per element — the usual target',
    ops: (n) => n * Math.log2(Math.max(n, 2)),
  },
  { id: 'on2', label: 'O(n²)', gloss: 'Every pair — fine only for small n', ops: (n) => n * n },
  {
    id: 'oexp',
    label: 'O(2ⁿ)',
    gloss: 'Every subset — needs n in the twenties',
    ops: (n) => 2 ** Math.min(n, 60),
  },
]

/** Constraint sizes as they actually appear in a LeetCode constraint block. */
export interface ConstraintStop {
  n: number
  /** How the bound is written on the problem page. */
  written: string
  /** The move this bound is telling you to make. */
  tell: string
}

export const CONSTRAINT_STOPS: ConstraintStop[] = [
  { n: 12, written: 'n ≤ 12', tell: 'Permutations are on the table — think n! or bitmask DP.' },
  { n: 20, written: 'n ≤ 20', tell: 'The classic bitmask tell: 2ⁿ over subsets is intended.' },
  { n: 100, written: 'n ≤ 100', tell: 'O(n³) fits. Floyd-Warshall, interval DP, anything cubic.' },
  { n: 1000, written: 'n ≤ 10³', tell: 'Quadratic DP is intended — LCS, edit distance, grid DP.' },
  { n: 3000, written: 'n ≤ 3·10³', tell: 'Still quadratic, but only just. Expect an O(n²) DP.' },
  {
    n: 100000,
    written: 'n ≤ 10⁵',
    tell: 'The most common bound. O(n log n) or better. Stop hunting for a clever O(n²).',
  },
  {
    n: 1000000,
    written: 'n ≤ 10⁶',
    tell: 'Linear or n log n with a small constant. Watch your allocations.',
  },
  {
    n: 1000000000,
    written: 'n ≤ 10⁹',
    tell: 'n is a *value*, not a length — binary search the answer, or find the maths.',
  },
]

export function isFeasible(cls: ComplexityClass, n: number): boolean {
  return cls.ops(n) <= OPS_BUDGET
}

/** The best class you can afford at this n — what to aim for. */
export function targetFor(n: number): ComplexityClass {
  const affordable = COMPLEXITY_CLASSES.filter((c) => isFeasible(c, n))
  return affordable[affordable.length - 1] ?? (COMPLEXITY_CLASSES[0] as ComplexityClass)
}

/**
 * The complexity a pattern characteristically lands on.
 *
 * Approximate by nature — a sliding window is O(n) but Segment Trees are
 * O(log n) *per query* — so these describe the shape you quote in the round,
 * not a proof.
 */
export const PATTERN_COMPLEXITY: Record<string, ComplexityId> = {
  'arrays-hashing': 'on',
  'prefix-sums': 'on',
  'two-pointers': 'on',
  'sliding-window': 'on',
  sorting: 'onlogn',
  intervals: 'onlogn',
  matrix: 'on',
  'string-manipulation': 'on',
  'string-algorithms': 'on',
  stack: 'on',
  'monotonic-stack': 'on',
  'binary-search': 'o1',
  'binary-search-answer': 'onlogn',
  'linked-lists': 'on',
  'binary-trees': 'on',
  'binary-search-trees': 'o1',
  tries: 'on',
  heaps: 'onlogn',
  'graph-traversal': 'on',
  'topological-sort': 'on',
  'union-find': 'on',
  'shortest-paths': 'onlogn',
  'minimum-spanning-tree': 'onlogn',
  'advanced-graphs': 'onlogn',
  'divide-and-conquer': 'onlogn',
  backtracking: 'oexp',
  greedy: 'onlogn',
  'dp-1d': 'on',
  'dp-grid-knapsack': 'on2',
  'dp-strings': 'on2',
  'dp-advanced': 'oexp',
  'math-geometry': 'o1',
  'bit-manipulation': 'o1',
  randomized: 'on',
  design: 'o1',
  ood: 'o1',
  concurrency: 'o1',
  'segment-tree': 'o1',
  'ordered-set': 'o1',
}

export const CLASS_BY_ID = new Map(COMPLEXITY_CLASSES.map((c) => [c.id, c]))

/** Tailwind token name for a class id — `text-o1`, `bg-onlogn`, etc. */
export function complexityVar(id: ComplexityId): string {
  return `var(--color-${id})`
}
