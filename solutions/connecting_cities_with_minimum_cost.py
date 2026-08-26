"""Connecting Cities With Minimum Cost — LeetCode 1135."""

from __future__ import annotations

META = {
    "pattern": "minimum-spanning-tree",
    "insight": "Kruskal on the given edges; the -1 case is free if the DSU tracks its component count instead of re-running a traversal.",
    "time": "O(E log E)",
    "space": "O(N)",
    "sections": [
        (
            "What it asks",
            """
LeetCode 1135 is premium, so the statement is not public — described here in
my own words. You are given `n` cities numbered `1..n` and a list of
`[city_a, city_b, cost]` connections. Choose a subset of connections so every
city can reach every other, at minimum total cost. If no subset achieves that,
return `-1`.

This is minimum spanning tree stated almost verbatim; the interesting part is
what the input is allowed to contain. Ask three things:

- **Are the cities 1-indexed?** They are, and it is the most common source of
  an off-by-one here.
- **Can there be parallel edges or self-loops?** Assume yes. Neither breaks
  Kruskal — a parallel edge is simply rejected once the endpoints are already
  joined, and a self-loop is rejected immediately — but say so rather than
  hoping.
- **Can the graph be disconnected?** Yes, and that is the whole point of the
  `-1` branch.
""",
        ),
        (
            "The insight",
            """
The edges are handed to you, `E` can be up to ~10⁴, and there is no geometry to
exploit. That makes this Kruskal's territory: sort the edges by cost and take
each one that joins two different components.

The cut property is the justification. Scanning in ascending cost, the first
edge that leaves a component is the cheapest edge crossing the cut between that
component and everything else, so it belongs to some MST. A disjoint-set union
answers "different components?" in near-constant time, so the sort dominates:
**O(E log E)**.

The part worth engineering is the `-1`. The lazy version runs a BFS at the end
to check connectivity. Instead, have the DSU carry a `components` counter that
decrements on every successful union — then "is it connected?" is a single
integer comparison, and the same counter lets you early-exit once `n - 1` edges
have been taken.

Prim also works, but only after you build an adjacency list from the edge list.
On a sparse, explicitly-given edge set Kruskal is the shorter correct answer.
""",
        ),
        (
            "Edge cases",
            """
- **`n = 1`.** Zero edges are needed and the answer is `0`, not `-1`. A
  connectivity check written as "did I take exactly `n - 1` edges?" gets this
  right; one written as "is the edge list non-empty?" does not.
- **1-indexing.** Sizing the DSU at `n` and indexing with city numbers walks
  off the end. Size it at `n + 1`, leave slot 0 unused, and remember to start
  the component count at `n`, not `n + 1` — otherwise the never-merged phantom
  node 0 makes a fully connected graph look disconnected forever.
- **Disconnected input** returns `-1` even when the given edges are cheap; the
  cost of the partial forest is not an answer.
- **Parallel edges** are handled by the union check, so do not pre-deduplicate
  by pair — if you keep the wrong duplicate you overpay.
- **Costs can be large**; the total is a sum of up to `n - 1` of them, so watch
  for 32-bit overflow in a language that has it. Python does not care.
- Sort with `sorted(...)`, not `connections.sort()`. Mutating the caller's list
  is a gratuitous side effect and the kind of thing a reviewer notices.
""",
        ),
    ],
}


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
        """False means a and b were already connected — a rejected edge."""
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


def minimum_cost(n: int, connections: list[list[int]]) -> int:
    dsu = UnionFind(n + 1)  # cities are 1-indexed; slot 0 is a placeholder
    dsu.components -= 1  # ... so do not let it count as a real component
    total = 0

    for city_a, city_b, cost in sorted(connections, key=lambda edge: edge[2]):
        if dsu.union(city_a, city_b):
            total += cost
            if dsu.components == 1:  # n - 1 edges taken, nothing left to join
                return total

    return total if dsu.components == 1 else -1


CASES = [
    ((3, [[1, 2, 5], [1, 3, 6], [2, 3, 1]]), 6),
    ((4, [[1, 2, 3], [3, 4, 4]]), -1),
    # A single city needs no edges at all.
    ((1, []), 0),
    ((2, []), -1),
    ((2, [[1, 2, 7]]), 7),
    # Parallel edges: the cheaper one must win.
    ((2, [[1, 2, 9], [1, 2, 4]]), 4),
    # Cheap chain beats the expensive shortcuts.
    ((4, [[1, 2, 1], [2, 3, 1], [3, 4, 1], [1, 4, 100], [1, 3, 50]]), 3),
    # A self-loop must be rejected, not counted.
    ((3, [[1, 1, 5], [1, 2, 2], [2, 3, 3]]), 5),
]


def solve(n: int, connections: list[list[int]]) -> int:
    return minimum_cost(n, connections)
