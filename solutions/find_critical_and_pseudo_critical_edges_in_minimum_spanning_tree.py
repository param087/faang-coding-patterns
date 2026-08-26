"""Find Critical and Pseudo-Critical Edges in Minimum Spanning Tree — LeetCode 1489."""

from __future__ import annotations

META = {
    "pattern": "minimum-spanning-tree",
    "insight": "Rerun Kruskal per edge: banning it and getting a worse tree means critical, forcing it in and still hitting base means pseudo.",
    "time": "O(E² · α(N))",
    "space": "O(N + E)",
    "sections": [
        (
            "What it asks",
            """
Given a weighted undirected graph, classify every edge:

- **critical** — it appears in *every* minimum spanning tree;
- **pseudo-critical** — it appears in *some* MST but not all.

Return the two lists of **original indices** (edges may be given in any order,
and the answer is in terms of where they sat in the input, not where they sit
after you sort).

The constraints are the design brief: `n ≤ 100`, `edges ≤ 200`. That is small
enough to say, honestly and immediately, "I am going to rebuild the MST twice
per edge", which is the intended solution and not a compromise.
""",
        ),
        (
            "The definitions are the problem",
            """
The wrong first answer, and it is very tempting: run Kruskal once, call the
edges it picked critical and the rest pseudo-critical.

That is only correct when all weights are distinct — in which case the MST is
unique, every tree edge is critical and nothing is pseudo-critical. The moment
there is a tie, Kruskal's choice among equal-weight edges is arbitrary, so
"the edge my sort happened to reach first" says nothing about whether it is in
*every* MST. A triangle with all weights 1 has three MSTs; no edge is critical
and all three are pseudo-critical.

So the classification has to be phrased as a counterfactual about MST *weight*,
not about one particular run:

- **critical** ⟺ deleting it makes the minimum spanning weight larger (or
  disconnects the graph entirely, which is the same thing with weight ∞);
- **pseudo-critical** ⟺ not critical, but forcing it into the tree still
  achieves the minimum weight.

Every edge is exactly one of critical, pseudo-critical, or neither — "neither"
being an edge too heavy to appear in any MST.
""",
        ),
        (
            "Why the quadratic answer is the right answer",
            """
One Kruskal run is O(E log E) for the sort plus O(E · α) for the unions. Sort
the index list **once**, up front, and each subsequent run is a bare O(E · α)
scan — no re-sorting.

That gives `2E + 1` runs: 401 at the constraint, each doing ≤ 200 union
operations, so roughly 8 · 10⁴ DSU calls. Microseconds.

Compare that with what you would need if `E` were 10⁵: 2 · 10⁵ Kruskal runs at
10⁵ operations each is 10¹⁰, and you would have to reach for the real theory —
build one MST, then an edge is non-critical iff it lies on a cycle of
equal-weight edges, which you detect with Tarjan's bridge-finding on each
weight class as it is added. Mentioning that you *know* the O(E log E) approach
exists, then writing the simple one because E ≤ 200, is a strong answer.
""",
        ),
        (
            "The insight",
            """
Compute `base` = the MST weight of the untouched graph. Then for edge `i`:

- **Exclude test.** Run Kruskal skipping edge `i`. If the result is worse than
  `base` — including "the graph fell apart", which you treat as ∞ — then no MST
  can do without it, so it is **critical**.
- **Include test.** Seed the DSU by unioning edge `i`'s endpoints and adding
  its weight, then run Kruskal normally over everything else. If the total
  still equals `base`, some MST contains it, so it is **pseudo-critical**.

The include test needs no special handling for edge `i` reappearing in the
scan: its endpoints are already joined, so the union fails and it is skipped
like any redundant edge.
""",
        ),
        (
            "The detail that decides it",
            """
**Test exclusion first and `continue`.** A critical edge also passes the
include test — forcing in an edge that every MST already contains obviously
reaches `base` — so an implementation that runs both tests independently
reports every critical edge in *both* lists. The categories are meant to be
disjoint, and the judge rejects it. This is the single most common wrong
submission on the problem.

**Sort indices, not edges.** The output is in terms of original positions, so
sorting `edges` in place destroys the very thing you have to report. Sort
`range(m)` by weight and carry the index through:

```python
order = sorted(range(m), key=lambda i: edges[i][2])
```

**Disconnection is ∞, not "skip it".** If banning edge `i` leaves the graph in
two pieces, the exclude test must fire. Return infinity from the helper when
the DSU has more than one component rather than returning the partial forest's
weight, which would compare as *less* than `base` and mark a bridge as not
critical — a silent, plausible-looking wrong answer.

**Do not mutate the input.** Every one of the `2E + 1` runs works from the same
`edges` list, so a helper that pops or reorders it poisons every later run.
""",
        ),
        (
            "Dry run",
            """
`n = 5`, edges (index: u-v @ w):

```
0: 0-1 @1   1: 1-2 @1   2: 2-3 @2   3: 0-3 @2   4: 0-4 @3   5: 3-4 @3   6: 1-4 @6
```

`base = 7` (take 0, 1, then one of {2, 3}, then one of {4, 5}).

- Ban edge 0: 0 and 1 can still be joined, but only via heavier edges — the
  best becomes 8. **Critical.** Same for edge 1.
- Ban edge 2: edge 3 substitutes at the same weight 2, total still 7. Not
  critical. Force edge 2 in: still 7. **Pseudo-critical.** Symmetrically for
  edge 3, and for the pair 4/5 at weight 3.
- Edge 6 at weight 6: banning it changes nothing, forcing it in gives 6 + (the
  cheapest tree on the rest) = 10 > 7. **Neither.**

Answer: `[[0, 1], [2, 3, 4, 5]]`. Note that edges 2 and 3 are interchangeable
and edges 4 and 5 are interchangeable — the ties are what make the second list
non-empty, and they are exactly what a single Kruskal run cannot see.
""",
        ),
        (
            "Follow-ups",
            """
- **"Now the graph has 10⁵ edges."** Build one MST, then for each weight class
  contract the components formed by lighter edges and run a bridge-finding pass
  over the equal-weight edges within it: bridges are critical, non-bridge tree
  edges are pseudo-critical. O(E log E).
- **"An edge's weight changes — recompute."** Increasing a tree edge's weight
  may swap it out for the cheapest edge across the cut it defines; decreasing a
  non-tree edge's weight may swap out the heaviest edge on its tree path. Both
  are O(n) with a link-cut tree or an LCA-with-max-edge table.
- **"Is the MST unique?"** Equivalent to "is the pseudo-critical list empty?",
  which is a much cheaper question — the standard test is whether any weight
  class ever offers more candidate edges than it consumes.
""",
        ),
    ],
}

INFINITY = float("inf")


class UnionFind:
    """DSU by rank with path compression, tracking live component count."""

    def __init__(self, size: int) -> None:
        self.parent = list(range(size))
        self.rank = [0] * size
        self.components = size

    def find(self, x: int) -> int:
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:  # path compression
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a: int, b: int) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        self.components -= 1
        return True


def find_critical_and_pseudo_critical_edges(
    n: int, edges: list[list[int]]
) -> list[list[int]]:
    m = len(edges)
    # Sort indices, never the edges themselves — the answer is in input order.
    order = sorted(range(m), key=lambda i: edges[i][2])

    def mst_weight(banned: int = -1, forced: int = -1) -> float:
        dsu = UnionFind(n)
        total = 0
        if forced >= 0:
            u, v, weight = edges[forced]
            dsu.union(u, v)
            total += weight
        for i in order:
            if i == banned:
                continue
            u, v, weight = edges[i]
            if dsu.union(u, v):  # a forced edge reappearing is rejected here
                total += weight
        # Disconnected must compare as worse than any real weight.
        return total if dsu.components == 1 else INFINITY

    base = mst_weight()
    critical: list[int] = []
    pseudo: list[int] = []

    for i in range(m):
        if mst_weight(banned=i) > base:
            critical.append(i)  # every MST needs it
            continue  # and must NOT also be reported as pseudo-critical
        if mst_weight(forced=i) == base:
            pseudo.append(i)  # some MST contains it

    return [critical, pseudo]


CASES = [
    (
        (
            5,
            [[0, 1, 1], [1, 2, 1], [2, 3, 2], [0, 3, 2], [0, 4, 3], [3, 4, 3], [1, 4, 6]],
        ),
        [[0, 1], [2, 3, 4, 5]],
    ),
    # All weights equal: four MSTs, so nothing is critical.
    ((4, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [0, 3, 1]]), [[], [0, 1, 2, 3]]),
    # A triangle of ties — the case that kills "one Kruskal run".
    ((3, [[0, 1, 1], [1, 2, 1], [0, 2, 1]]), [[], [0, 1, 2]]),
    # Distinct weights: the MST is unique, so tree edges are all critical.
    ((3, [[0, 1, 1], [1, 2, 2], [0, 2, 3]]), [[0, 1], []]),
    # A bridge must be caught by the disconnection branch.
    ((2, [[0, 1, 5]]), [[0], []]),
    # Parallel duplicate edges are interchangeable, hence pseudo-critical.
    ((2, [[0, 1, 3], [0, 1, 3]]), [[], [0, 1]]),
    # Edge 3 is too heavy for any MST: neither list.
    ((4, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [0, 2, 5]]), [[0, 1, 2], []]),
    # A heavy edge listed first: indices must survive the sort, and edge 3 is
    # the only cheap way to reach node 3 despite sitting among ties.
    ((4, [[0, 3, 9], [0, 1, 2], [1, 2, 2], [2, 3, 2], [0, 2, 2]]), [[3], [1, 2, 4]]),
]


def solve(n: int, edges: list[list[int]]) -> list[list[int]]:
    return find_critical_and_pseudo_critical_edges(n, edges)
