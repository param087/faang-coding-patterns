"""Redundant Connection — LeetCode 684."""

from __future__ import annotations

META = {
    "pattern": "union-find",
    "insight": "union() returning False IS the cycle test — the first edge whose endpoints are already connected is the answer.",
    "time": "O(n · α(n))",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
A tree with one extra edge added. Find the edge that can be removed to make it
a tree again. If several answers exist, return the one appearing **last** in
the input.

Ask: is the graph undirected (**yes** — the directed version, Redundant
Connection II, is genuinely harder); is exactly one extra edge guaranteed
(yes); are nodes 1-indexed (yes).
""",
        ),
        (
            "The insight",
            """
Add edges one at a time. The first edge whose two endpoints are **already
connected** is the one closing the cycle.

And because you process in input order, that edge is automatically the last
such edge — the tie-break rule is satisfied for free rather than needing a
second pass.
""",
        ),
        (
            "union() returning False is the whole answer",
            """
This is the reason union-find and cycle detection are always taught together.

`union(a, b)` returns `False` exactly when `a` and `b` shared a root already —
which is exactly "this edge creates a cycle". No separate cycle-detection
logic is needed.

The same boolean is what drives Kruskal's MST (skip the edge) and Graph Valid
Tree (fail immediately).
""",
        ),
        (
            "Why not DFS",
            """
You could DFS before each insertion to test connectivity: O(V·E).

DSU makes each test effectively O(1), so the whole thing is O(E). Say the
comparison — the question is really "do you know when connectivity is
*dynamic*".
""",
        ),
        (
            "The 1-indexing",
            """
Nodes are numbered `1..n`, so size the parent array `n + 1` and ignore index
0. Off-by-one here produces an index error on the last node, which is an
annoying way to fail an easy question.
""",
        ),
        (
            "Dry run",
            """
`[[1,2],[1,3],[2,3]]`

- `union(1,2)` → True.
- `union(1,3)` → True.
- `union(2,3)` → **False**: 2 and 3 already share a root via 1.

Answer `[2,3]`.
""",
        ),
        (
            "Follow-ups",
            """
- **Redundant Connection II** (directed). Much harder: a node may have two
  parents, *or* there may be a cycle, *or* both — and the three cases need
  different answers. Say that it is a different problem rather than trying to
  adapt this one.
- **Graph Valid Tree** — `n - 1` edges *and* no union returning False.
""",
        ),
    ],
}


class UnionFind:
    def __init__(self, n: int) -> None:
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x: int) -> int:
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:  # path compression
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a: int, b: int) -> bool:
        """False means they were already connected — i.e. this edge is a cycle."""
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


def find_redundant_connection(edges: list[list[int]]) -> list[int]:
    dsu = UnionFind(len(edges) + 1)  # nodes are 1-indexed

    for a, b in edges:
        if not dsu.union(a, b):
            return [a, b]  # first failure, and therefore the last valid answer

    return []


CASES = [
    (([[1, 2], [1, 3], [2, 3]],), [2, 3]),
    (([[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]],), [1, 4]),
    (([[1, 2], [2, 1]],), [2, 1]),
    (([[1, 2], [1, 3], [1, 4], [3, 4]],), [3, 4]),
]


def solve(edges: list[list[int]]) -> list[int]:
    return find_redundant_connection(edges)
