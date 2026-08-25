/**
 * The 39-pattern taxonomy — the spine of the whole site.
 *
 * Wider than NeetCode's 19 buckets on purpose. The patterns NeetCode folds
 * into something else (monotonic stack inside Stack, union-find inside
 * Graphs, prefix sums inside Arrays) get their own page here, because in a
 * real round they are recognised and reached for independently. Two of them
 * — Design and OOD — have no NeetCode bucket at all, yet Design is one of
 * the highest-frequency FAANG SDE-2 categories.
 *
 * `signals` drives auto-classification for the long tail: each LeetCode topic
 * tag carries a weight, the pattern with the highest total wins. Weights are
 * inverse to how generic a tag is — `array` (2,237 problems) is worth 1,
 * `monotonic-stack` (73 problems) is worth 90 — so a specific tag always
 * beats a pile of generic ones. Anything in a pattern's Core list is
 * hand-assigned in CATALOGUE.md and bypasses this entirely.
 */

export interface PatternGroup {
  id: string
  name: string
  /** Shown under the group heading in the nav rail and on the landing page. */
  blurb: string
}

export interface Pattern {
  id: string
  name: string
  group: string
  /** One line, imperative, on what the pattern *is*. Used on cards and in search. */
  tagline: string
  /** LeetCode topic tags that suggest this pattern, with confidence weights. */
  signals: Record<string, number>
  /** NeetCode buckets that map here. Adds a modest bonus during classification. */
  neetcode?: string[]
}

export const GROUPS: PatternGroup[] = [
  {
    id: 'linear',
    name: 'Arrays, strings & linear scans',
    blurb: 'The patterns that turn a nested loop into a single pass. Where most rounds start.',
  },
  {
    id: 'stack',
    name: 'Stacks & queues',
    blurb:
      'Deferring work until you know what to do with it — and the linear-time trick that follows.',
  },
  {
    id: 'search',
    name: 'Binary search',
    blurb: 'Halving a sorted array, and the harder move: halving the space of possible answers.',
  },
  {
    id: 'structures',
    name: 'Linked structures, trees & heaps',
    blurb: 'Pointer surgery, recursion over trees, and keeping only the k things that matter.',
  },
  {
    id: 'graphs',
    name: 'Graphs',
    blurb: 'Traversal, ordering, connectivity and weighted paths — the densest FAANG category.',
  },
  {
    id: 'recursion',
    name: 'Recursion, backtracking & greedy',
    blurb:
      'Explore-and-undo, divide-and-conquer, and knowing when the locally-best move is provably right.',
  },
  {
    id: 'dp',
    name: 'Dynamic programming',
    blurb: 'Finding the state, writing the recurrence, then folding the table down a dimension.',
  },
  {
    id: 'longtail',
    name: 'Math, bits, design & the long tail',
    blurb: 'The categories that decide rounds precisely because most candidates skip them.',
  },
]

export const PATTERNS: Pattern[] = [
  // ---------------------------------------------------------------- linear
  {
    id: 'arrays-hashing',
    name: 'Arrays & Hashing',
    group: 'linear',
    tagline: 'Trade memory for time: a dict or set collapses an O(n²) scan to O(n).',
    signals: { 'hash-table': 20, counting: 18, array: 1, string: 1, 'hash-function': 12 },
    neetcode: ['Arrays & Hashing'],
  },
  {
    id: 'prefix-sums',
    name: 'Prefix Sums & Difference Arrays',
    group: 'linear',
    tagline: 'Precompute cumulative totals so any range answers in O(1).',
    signals: { 'prefix-sum': 60, array: 1 },
  },
  {
    id: 'two-pointers',
    name: 'Two Pointers',
    group: 'linear',
    tagline: 'Two indices moving under an invariant — opposite ends, same direction, or fast/slow.',
    signals: { 'two-pointers': 50, 'floyds-cycle-finding-algorithm': 40 },
    neetcode: ['Two Pointers'],
  },
  {
    id: 'sliding-window',
    name: 'Sliding Window',
    group: 'linear',
    tagline: 'A window that grows on the right and shrinks on the left to hold an invariant.',
    signals: { 'sliding-window': 70 },
    neetcode: ['Sliding Window'],
  },
  {
    id: 'sorting',
    name: 'Sorting & Custom Comparators',
    group: 'linear',
    tagline: 'Most of the work is choosing the key; the sort itself is one line.',
    signals: {
      sorting: 15,
      'counting-sort': 40,
      'bucket-sort': 40,
      'radix-sort': 40,
      'merge-sort': 25,
      quicksort: 30,
      'bubble-sort': 30,
      timsort: 30,
      'tournament-sort': 30,
      sort: 20,
    },
  },
  {
    id: 'intervals',
    name: 'Intervals & Sweep Line',
    group: 'linear',
    tagline: 'Sort by an endpoint, then sweep — merging, counting overlaps, or booking rooms.',
    signals: { 'sweep-line': 70, 'line-sweep': 70 },
    neetcode: ['Intervals'],
  },
  {
    id: 'matrix',
    name: 'Matrix & Simulation',
    group: 'linear',
    tagline:
      'Follow the rules exactly, in place, without an off-by-one — grids, spirals, state machines.',
    signals: { matrix: 25, simulation: 30 },
  },
  {
    id: 'string-manipulation',
    name: 'String Parsing & Manipulation',
    group: 'linear',
    tagline: 'Tokenise, evaluate, encode — the problems that are really small parsers.',
    signals: { string: 3, 'bracket-sequences': 30 },
  },
  {
    id: 'string-algorithms',
    name: 'String Algorithms',
    group: 'linear',
    tagline: 'KMP, Z-function, rolling hashes and Manacher — linear-time substring machinery.',
    signals: {
      'string-matching': 55,
      'rolling-hash': 55,
      'knuth-morris-pratt-algorithm': 80,
      'z-algorithm': 80,
      manacher: 80,
      'aho-corasick-algorithm': 80,
      'suffix-array': 60,
      'suffix-tree': 60,
      'suffix-automaton': 60,
      'boyer-moore-string-search-algorithm': 60,
      'lexicographically-minimal-string-rotation': 60,
      'lyndon-factorization': 60,
      'palindromic-tree': 60,
    },
  },

  // ----------------------------------------------------------------- stack
  {
    id: 'stack',
    name: 'Stack Fundamentals',
    group: 'stack',
    tagline: 'Defer work until the matching event arrives — brackets, RPN, nested structures.',
    signals: { stack: 22, queue: 15 },
    neetcode: ['Stack'],
  },
  {
    id: 'monotonic-stack',
    name: 'Monotonic Stack & Deque',
    group: 'stack',
    tagline: 'Keep the stack sorted and every "next greater" question becomes one pass.',
    signals: { 'monotonic-stack': 90, 'monotonic-queue': 90, 'cartesian-tree': 40 },
  },

  // ---------------------------------------------------------------- search
  {
    id: 'binary-search',
    name: 'Binary Search on Arrays',
    group: 'search',
    tagline: 'One template, three bounds. Most bugs live in the loop condition.',
    signals: { 'binary-search': 25 },
    neetcode: ['Binary Search'],
  },
  {
    id: 'binary-search-answer',
    name: 'Binary Search on the Answer',
    group: 'search',
    tagline: 'Guess the answer, ask "is it feasible?", halve. The step most candidates miss.',
    signals: { 'ternary-search': 50 },
  },

  // ------------------------------------------------------------ structures
  {
    id: 'linked-lists',
    name: 'Linked Lists',
    group: 'structures',
    tagline: 'Dummy heads, pointer rewiring, and never losing the node you still need.',
    signals: { 'linked-list': 45, 'doubly-linked-list': 45 },
    neetcode: ['Linked List'],
  },
  {
    id: 'binary-trees',
    name: 'Binary Trees: Traversal & Recursion',
    group: 'structures',
    tagline: 'Decide what each node returns to its parent, and the recursion writes itself.',
    signals: {
      'binary-tree': 25,
      tree: 18,
      'depth-first-search': 8,
      'breadth-first-search': 8,
      'lowest-common-ancestor': 50,
      'binary-lifting': 45,
    },
    neetcode: ['Trees'],
  },
  {
    id: 'binary-search-trees',
    name: 'Binary Search Trees',
    group: 'structures',
    tagline:
      'The in-order traversal is sorted — almost every BST problem is that fact in disguise.',
    signals: { 'binary-search-tree': 55, treap: 40, 'splay-tree': 40 },
  },
  {
    id: 'tries',
    name: 'Tries',
    group: 'structures',
    tagline: 'A tree keyed by character — or by bit, which is how you get max-XOR in O(32n).',
    // 45, not 60: LeetCode tags `trie` on plenty of problems where it is merely
    // an alternative approach (Word Break is really 1-D DP).
    signals: { trie: 45 },
    neetcode: ['Tries'],
  },
  {
    id: 'heaps',
    name: 'Heaps & Priority Queues',
    group: 'structures',
    tagline: 'Top-k, k-way merge, and the two-heap trick for a running median.',
    signals: { 'heap-priority-queue': 40, 'data-stream': 35 },
    neetcode: ['Heap / Priority Queue'],
  },

  // ---------------------------------------------------------------- graphs
  {
    id: 'graph-traversal',
    name: 'Graph Traversal (BFS & DFS)',
    group: 'graphs',
    tagline: 'Islands, flood fill, multi-source BFS and shortest hops on an unweighted grid.',
    signals: {
      graph: 20,
      'depth-first-search': 14,
      'breadth-first-search': 14,
      '0-1-bfs': 50,
      'bidirectional-search': 45,
      'bipartite-graph': 45,
      'graph-coloring': 40,
      'matching-graph': 35,
      'maximum-matching': 35,
      'perfect-matching': 35,
    },
    neetcode: ['Graphs'],
  },
  {
    id: 'topological-sort',
    name: 'Topological Sort & Cycle Detection',
    group: 'graphs',
    tagline: 'Order the tasks, or prove you cannot. Kahn’s algorithm plus a cycle check.',
    signals: { 'topological-sort': 75, 'directed-acyclic-graph': 55 },
  },
  {
    id: 'union-find',
    name: 'Union-Find (DSU)',
    group: 'graphs',
    tagline:
      'Merge sets in near-constant time — connectivity, Kruskal, and "are these the same thing?".',
    signals: { 'union-find': 45 },
  },
  {
    id: 'shortest-paths',
    name: 'Shortest Paths',
    group: 'graphs',
    tagline:
      'Dijkstra when weights are non-negative, Bellman-Ford when they are not, Floyd for all pairs.',
    signals: {
      'shortest-path': 60,
      dijkstra: 80,
      'bellman-ford-algorithm': 80,
      'floyd-warshall-algorithm': 80,
      'a-search': 55,
      'heuristic-search': 45,
      'k-shortest-path': 60,
    },
    neetcode: ['Advanced Graphs'],
  },
  {
    id: 'minimum-spanning-tree',
    name: 'Minimum Spanning Tree',
    group: 'graphs',
    tagline: 'Connect everything for the least cost — Kruskal with DSU, or Prim with a heap.',
    signals: {
      'minimum-spanning-tree': 85,
      'prims-algorithm': 85,
      'kruskals-algorithm': 85,
      'boruvkas-algorithm': 85,
    },
  },
  {
    id: 'advanced-graphs',
    name: 'Advanced Graphs',
    group: 'graphs',
    tagline: 'Bridges, SCCs, Eulerian paths and flow — rare, but decisive when they appear.',
    signals: {
      'strongly-connected-component': 80,
      'tarjans-scc-algorithm': 85,
      'kosarajus-algorithm': 85,
      'eulerian-path': 80,
      'eulerian-circuit': 80,
      'eulerian-graph': 80,
      'semi-eulerian-graph': 80,
      'flow-network': 80,
      'maximum-flow': 80,
      'minimum-cut': 80,
      'minimum-cost-flow': 80,
      'dinics-algorithm': 85,
      'edmonds-karp-algorithm': 85,
      'push-relabel-algorithm': 85,
      'successive-shortest-path-algorithm': 80,
      'mpm-algorithm': 85,
      'hungarian-algorithm': 80,
      'articulation-point': 80,
      'bridge-graph': 80,
      'biconnected-component': 80,
      'hamiltonian-path': 70,
      'planar-graph': 70,
    },
  },

  // ------------------------------------------------------------- recursion
  {
    id: 'divide-and-conquer',
    name: 'Recursion & Divide and Conquer',
    group: 'recursion',
    tagline: 'Split, solve, merge — and quickselect, which only recurses on the half that matters.',
    signals: { 'divide-and-conquer': 45, recursion: 25, quickselect: 60, 'k-d-tree': 40 },
  },
  {
    id: 'backtracking',
    name: 'Backtracking',
    group: 'recursion',
    tagline: 'Choose, explore, un-choose. The whole game is pruning the branches that cannot win.',
    signals: {
      backtracking: 55,
      'meet-in-the-middle': 50,
      'algorithm-x': 60,
      'dancing-links': 60,
      'brute-force-search': 30,
    },
    neetcode: ['Backtracking'],
  },
  {
    id: 'greedy',
    name: 'Greedy & Exchange Arguments',
    group: 'recursion',
    tagline: 'Take the locally-best move — and be ready to argue why that is globally optimal.',
    signals: { greedy: 22, 'boyer-moore-majority-vote-algorithm': 50, 'pigeonhole-principle': 30 },
    neetcode: ['Greedy'],
  },

  // -------------------------------------------------------------------- dp
  {
    id: 'dp-1d',
    name: '1-D Dynamic Programming',
    group: 'dp',
    tagline: 'One array, one recurrence. Climbing stairs, house robber, word break, LIS.',
    signals: {
      'dynamic-programming': 12,
      memoization: 12,
      'longest-increasing-subsequence': 55,
    },
    neetcode: ['1-D Dynamic Programming'],
  },
  {
    id: 'dp-grid-knapsack',
    name: 'Grid & Knapsack DP',
    group: 'dp',
    tagline: 'Two dimensions of state — paths through a grid, and every flavour of knapsack.',
    signals: {
      'knapsack-problem': 60,
      '0-1-knapsack': 65,
      'complete-knapsack': 65,
      'multiple-knapsack': 65,
      'mixed-knapsack': 65,
    },
    neetcode: ['2-D Dynamic Programming'],
  },
  {
    id: 'dp-strings',
    name: 'DP on Strings & Subsequences',
    group: 'dp',
    tagline: 'Edit distance, LCS, wildcard matching — two pointers into two strings as state.',
    signals: { 'longest-common-subsequence': 65 },
  },
  {
    id: 'dp-advanced',
    name: 'Advanced DP',
    group: 'dp',
    tagline: 'Bitmask, tree, interval and digit DP, state machines, and minimax game theory.',
    signals: {
      bitmask: 40,
      'dp-on-trees': 65,
      'game-theory': 60,
      'minimax-algorithm': 60,
      'zero-sum-game': 55,
      'impartial-game': 60,
      'nim-game': 65,
      'sprague-grundy-theorem': 70,
      'probability-and-statistics': 25,
      'li-chao-tree': 55,
    },
  },

  // -------------------------------------------------------------- longtail
  {
    id: 'math-geometry',
    name: 'Math & Geometry',
    group: 'longtail',
    tagline: 'GCD, primes, modular arithmetic, overflow — and the geometry that actually shows up.',
    signals: {
      math: 8,
      'number-theory': 30,
      geometry: 45,
      combinatorics: 30,
      enumeration: 6,
      'greatest-common-divisor': 45,
      'euclidean-algorithm': 45,
      'extended-euclidean-algorithm': 50,
      'prime-factorization': 45,
      'primality-test': 45,
      'sieve-theory': 50,
      'prime-number-sieve': 50,
      'fermats-little-theorem': 50,
      'eulers-totient-function': 50,
      'eulers-theorem': 50,
      'least-common-multiple': 45,
      'inclusion-exclusion-principle': 45,
      polygons: 50,
      'convex-hull': 55,
      triangulation: 50,
      'nearest-pair-of-points': 50,
      'minimum-enclosing-circle': 50,
      'linear-algebra': 45,
      'newtons-method': 45,
      'bezouts-lemma': 50,
      brainteaser: 20,
    },
    neetcode: ['Math & Geometry'],
  },
  {
    id: 'bit-manipulation',
    name: 'Bit Manipulation',
    group: 'longtail',
    tagline: 'XOR cancellation, masks as sets, and reading n & (n-1) without flinching.',
    signals: { 'bit-manipulation': 30 },
    neetcode: ['Bit Manipulation'],
  },
  {
    id: 'randomized',
    name: 'Randomized Algorithms & Sampling',
    group: 'longtail',
    tagline:
      'Reservoir sampling, weighted pick, and shuffling correctly under a streaming constraint.',
    signals: {
      randomized: 70,
      'reservoir-sampling': 85,
      'rejection-sampling': 80,
    },
  },
  {
    id: 'design',
    name: 'Design (Data Structures)',
    group: 'longtail',
    tagline: 'Build a class to a latency contract: LRU, LFU, TimeMap, iterators, rate limiters.',
    // `design` is one of the few LeetCode tags that names the category rather
    // than an approach — if it is present, the problem really is a design problem.
    signals: { design: 65, iterator: 60 },
  },
  {
    id: 'ood',
    name: 'OOD in the Coding Round',
    group: 'longtail',
    tagline: 'Parking lot, elevator, card deck — modelling under a 35-minute clock.',
    signals: {},
  },
  {
    id: 'concurrency',
    name: 'Concurrency & Multithreading',
    group: 'longtail',
    tagline: 'Locks, semaphores and conditions — asked far more often than candidates prepare for.',
    signals: { concurrency: 90 },
  },
  {
    id: 'segment-tree',
    name: 'Segment Trees & Fenwick',
    group: 'longtail',
    tagline: 'Range query with point or range update, in O(log n). Plus lazy propagation.',
    signals: {
      'segment-tree': 70,
      'binary-indexed-tree': 75,
      'range-minimum-maximum-query': 70,
      'sqrt-decomposition': 60,
      'sparse-table': 65,
      'persistent-data-structure': 60,
    },
  },
  {
    id: 'ordered-set',
    name: 'Ordered Set & TreeMap Patterns',
    group: 'longtail',
    tagline: 'Floor/ceiling queries on a live set — trivial in Java, a real decision in Python.',
    signals: { 'ordered-set': 55 },
  },
]

/**
 * Tag *combinations* that identify a pattern better than any single tag.
 *
 * LeetCode tags every approach that works, not the canonical one, so a lone
 * high-weight tag can mislead — Number of Islands carries `union-find` even
 * though nobody reaches for DSU first. When every tag in `all` is present,
 * the bonus goes to `pattern`.
 */
export const COMBOS: { all: string[]; pattern: string; bonus: number }[] = [
  // Tagged for both traversals at once ⇒ it is a traversal problem.
  { all: ['depth-first-search', 'breadth-first-search'], pattern: 'graph-traversal', bonus: 55 },
  { all: ['matrix', 'depth-first-search'], pattern: 'graph-traversal', bonus: 35 },
  { all: ['matrix', 'breadth-first-search'], pattern: 'graph-traversal', bonus: 35 },
  // Trees own their own traversals; don't let the grid rules steal them.
  { all: ['binary-tree', 'depth-first-search'], pattern: 'binary-trees', bonus: 45 },
  { all: ['tree', 'breadth-first-search'], pattern: 'binary-trees', bonus: 40 },
  // Explicit memoised recursion is the DP tell.
  { all: ['dynamic-programming', 'memoization'], pattern: 'dp-1d', bonus: 25 },
  { all: ['dynamic-programming', 'matrix'], pattern: 'dp-grid-knapsack', bonus: 35 },
  { all: ['dynamic-programming', 'string'], pattern: 'dp-strings', bonus: 30 },
  { all: ['dynamic-programming', 'bitmask'], pattern: 'dp-advanced', bonus: 40 },
  { all: ['dynamic-programming', 'tree'], pattern: 'dp-advanced', bonus: 35 },
  // A sorted structure plus binary search on it is the ordered-set signature.
  { all: ['ordered-set', 'binary-search'], pattern: 'ordered-set', bonus: 30 },
  { all: ['design', 'ordered-set'], pattern: 'design', bonus: 25 },
  // Window problems tagged with a monotonic structure are deque problems.
  { all: ['sliding-window', 'monotonic-queue'], pattern: 'monotonic-stack', bonus: 40 },
  { all: ['string', 'sliding-window'], pattern: 'sliding-window', bonus: 25 },
  // Sorting an array of pairs and sweeping it.
  { all: ['sorting', 'sweep-line'], pattern: 'intervals', bonus: 45 },
  { all: ['greedy', 'sweep-line'], pattern: 'intervals', bonus: 40 },
  // Recursive descent over an expression is parsing, not divide-and-conquer.
  { all: ['string', 'stack', 'recursion'], pattern: 'string-manipulation', bonus: 45 },
  // Small on purpose: Valid Parentheses is `string` + `stack` and belongs to
  // Stack Fundamentals, so this must not out-score the plain `stack` signal.
  { all: ['string', 'stack'], pattern: 'string-manipulation', bonus: 12 },
]

/** Tags that mean "not a DSA coding-round problem" — SQL and shell challenges. */
export const EXCLUDED_TAGS = new Set(['database', 'shell'])

export const PATTERN_BY_ID = new Map(PATTERNS.map((p) => [p.id, p]))
export const GROUP_BY_ID = new Map(GROUPS.map((g) => [g.id, g]))

/** Patterns in nav order, grouped. */
export function patternsByGroup(): { group: PatternGroup; patterns: Pattern[] }[] {
  return GROUPS.map((group) => ({
    group,
    patterns: PATTERNS.filter((p) => p.group === group.id),
  }))
}
