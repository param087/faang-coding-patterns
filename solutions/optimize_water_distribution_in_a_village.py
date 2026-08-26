"""Optimize Water Distribution in a Village — LeetCode 1168."""

from __future__ import annotations

META = {
    "pattern": "minimum-spanning-tree",
    "insight": "Digging a well is a pipe to an imaginary node 0 that already has water — then the answer is one plain MST over n+1 nodes.",
    "time": "O((N + P) log (N + P))",
    "space": "O(N + P)",
    "sections": [
        (
            "What it asks",
            """
LeetCode 1168 is premium, so the statement is not public — described here in
my own words. There are `n` houses, numbered `1..n`. Each house can get water
one of two ways: dig a well inside it at cost `wells[i - 1]`, or lay a pipe
from a house that already has water, where the allowed pipes and their costs
are given as `[house_a, house_b, cost]`. Every house must end up with water.
Return the minimum total cost.

The reason this is rated Hard is that it does not *look* like a graph problem:
you have two different kinds of cost, one attached to nodes and one attached to
edges, and minimum spanning tree only knows about edges.

Worth clarifying: pipes are undirected (water flows either way once a well
exists somewhere on that component), the same pair can appear more than once
with different costs, and `n` and the number of pipes are both up to 10⁴.
""",
        ),
        (
            "The insight",
            """
Invent a **virtual node 0** — a reservoir that is already full — and turn every
well into an edge from that node:

```
dig a well at house i for cost w  ==  a pipe from node 0 to node i costing w
```

Now every cost in the problem is an edge cost, and "every house has water"
becomes "every house is connected to node 0". Connect `n + 1` nodes at minimum
total cost: that is a minimum spanning tree, and Kruskal with a DSU solves it
in one pass over `n + p` edges.

The transformation is exact, not an approximation. In any spanning tree of the
augmented graph, the edges incident to node 0 are exactly the houses that get
wells, and the rest are pipes — and every valid watering plan corresponds to
one such tree. Removing a cycle edge never makes a plan invalid, so the optimal
plan is always a tree.

Two consequences that people miss:

- **The augmented graph is always connected**, because every house has a well
  edge. So there is no `-1` case and no connectivity check to write.
- **The answer is not "dig the cheapest well and pipe outwards"**. That is a
  shortest-path-from-0 answer (Dijkstra), and it minimises the cost *per house*
  rather than the total. On `wells = [1, 100]`, `pipes = [[1, 2, 5]]` both give
  6, but on `wells = [1, 2]`, `pipes = [[1, 2, 5]]` the MST digs both wells for
  3 while a "one well plus pipes" reflex pays 6. Say why MST rather than
  Dijkstra out loud — it is the discriminating question in this interview.
""",
        ),
        (
            "The traps",
            """
- **Off-by-one on the wells array.** Houses are 1-indexed and `wells` is
  0-indexed. `enumerate(wells, start=1)` gets it right in one place; doing the
  arithmetic inline in two places gets it wrong in one of them.
- **Sizing the DSU at `n`.** It needs `n + 1` slots because node 0 is real
  here, not a placeholder — and the tree has `n` edges, not `n - 1`.
- **A pipe cheaper than both its wells is still not automatically taken.** It
  is taken only if it joins two different components; a pipe inside an already
  watered component is redundant no matter how cheap. The union check is doing
  real work, not just deduplication.
- **A pipe more expensive than digging** is simply never taken — no special
  casing, and no pre-filtering `pipes` against `wells` (which is a tempting
  optimisation that is easy to get subtly wrong when both endpoints are cheap).
- **Parallel pipes** between the same pair with different costs: sorting means
  the cheapest is seen first and the rest are rejected. Do not deduplicate by
  key and accidentally keep the last one.
- **`n = 1`**: the answer is `wells[0]`, and the code produces it with no
  special case — one edge, `0 → 1`.
- If `p` were much larger than `n²` you would prefer Prim with a heap, but at
  these constraints the sort dominates either way.
""",
        ),
    ],
}


class UnionFind:
    """DSU by rank with path compression."""

    def __init__(self, size: int) -> None:
        self.parent = list(range(size))
        self.rank = [0] * size

    def find(self, x: int) -> int:
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:  # path compression
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a: int, b: int) -> bool:
        """False means a and b already share water — a redundant edge."""
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


def min_cost_to_supply_water(n: int, wells: list[int], pipes: list[list[int]]) -> int:
    # Node 0 is the imaginary reservoir; a well becomes an edge 0 -> house.
    edges = [(cost, 0, house) for house, cost in enumerate(wells, start=1)]
    edges += [(cost, a, b) for a, b, cost in pipes]
    edges.sort()  # local list, so the caller's pipes are untouched

    dsu = UnionFind(n + 1)  # node 0 is real here, not a placeholder
    total = 0
    taken = 0

    for cost, a, b in edges:
        if dsu.union(a, b):
            total += cost
            taken += 1
            if taken == n:  # n edges span n + 1 nodes; nothing left to connect
                break

    return total


CASES = [
    ((3, [1, 2, 2], [[1, 2, 1], [2, 3, 1]]), 3),
    ((2, [1, 1], [[1, 2, 1]]), 2),
    # One well plus pipes loses to digging everywhere.
    ((2, [1, 2], [[1, 2, 5]]), 3),
    ((2, [5, 9], [[1, 2, 2]]), 7),
    # No pipes at all: every house pays for its own well.
    ((4, [10, 10, 10, 10], []), 40),
    # One cheap well feeding the rest by pipe.
    ((3, [1, 10, 10], [[1, 2, 2], [1, 3, 3]]), 6),
    # Parallel pipes: the cheaper one must be the one that survives.
    ((2, [3, 3], [[1, 2, 5], [1, 2, 1]]), 4),
    # Every pipe dearer than a well, so all pipes are ignored.
    ((3, [2, 2, 2], [[1, 2, 9], [2, 3, 9]]), 6),
    ((1, [7], []), 7),
]


def solve(n: int, wells: list[int], pipes: list[list[int]]) -> int:
    return min_cost_to_supply_water(n, wells, pipes)
