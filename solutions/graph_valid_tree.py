"""Graph Valid Tree — LeetCode 261."""

from __future__ import annotations

META = {
    "pattern": "union-find",
    "insight": "A tree is exactly n-1 edges AND no cycle — check the edge count first, then let union() returning False reject the rest.",
    "time": "O(n + e · α(n))",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
*(Premium problem — the statement is not public, so this is the task in my own
words.)* Given `n` nodes labelled `0 .. n-1` and a list of undirected edges,
decide whether the graph is a **valid tree**: connected, and with no cycle.

Worth asking: are duplicate edges possible? LeetCode says no, and that matters
more than it looks — `[[0,1],[0,1]]` is two edges on two nodes, so it passes
any count-only check while being an obvious cycle. Confirm it, or handle it.
""",
        ),
        (
            "The insight",
            """
A tree on `n` nodes is characterised by **any two** of these three facts:

1. connected,
2. acyclic,
3. exactly `n - 1` edges.

So test (3) with one comparison, then test (2) with the DSU — and connectivity
comes free:

```
if len(edges) != n - 1: return False
for a, b in edges:
    if not union(a, b): return False   # cycle
return True
```

The `n - 1` guard is not an optimisation, it is half the proof. With fewer
than `n - 1` edges the graph cannot be connected; with more it must contain a
cycle. Once the count is right, "no cycle" and "connected" are equivalent, so
one acyclicity check settles both.

`union(a, b)` returning `False` means `a` and `b` already shared a root — the
edge closes a cycle — which is the same primitive that answers Redundant
Connection and drives Kruskal's MST.
""",
        ),
        (
            "The case that breaks the naive version",
            """
Checking only the edge count is the standard wrong answer. It is *necessary*
but not *sufficient*:

`n = 5`, `edges = [[0,1],[1,2],[0,2],[3,4]]`

That is 4 edges and `n - 1 = 4`, so a count-only check says "valid tree". It is
not: `{0,1,2}` is a triangle and `{3,4}` is a separate component. The DSU
catches it — `union(0, 2)` returns `False` because 0 and 2 are already joined
through 1.

The mirror-image mistake is checking only for cycles: `n = 4`,
`edges = [[0,1],[2,3]]` is acyclic but is two components, and the count check
(`2 != 3`) is what rejects it.

Also: if you skip the count check and instead verify connectivity by counting
distinct roots at the end, that is equally correct and costs an extra O(n·α(n))
pass — but then you *must* still reject cycles, so you have not saved anything.
Do the cheap comparison first.
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
        """False means they already shared a root — i.e. this edge closes a cycle."""
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


def valid_tree(n: int, edges: list[list[int]]) -> bool:
    if len(edges) != n - 1:  # half the proof: too few, or guaranteed cycle
        return False

    dsu = UnionFind(n)
    return all(dsu.union(a, b) for a, b in edges)


CASES = [
    ((5, [[0, 1], [0, 2], [0, 3], [1, 4]]), True),
    ((5, [[0, 1], [1, 2], [2, 3], [1, 3], [1, 4]]), False),  # 5 edges > n - 1
    ((5, [[0, 1], [1, 2], [0, 2], [3, 4]]), False),  # right count, cycle + split
    ((4, [[0, 1], [2, 3]]), False),  # acyclic but disconnected
    ((2, [[0, 1]]), True),
    ((2, []), False),
    ((1, []), True),
    ((3, [[0, 1], [1, 2]]), True),
]


def solve(n: int, edges: list[list[int]]) -> bool:
    return valid_tree(n, edges)
