"""Number of Connected Components in an Undirected Graph — LeetCode 323."""

from __future__ import annotations

META = {
    "pattern": "union-find",
    "insight": "Start the count at n and subtract one for every union that actually merges — no traversal, no visited set.",
    "time": "O(n + e · α(n))",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
*(Premium problem — the statement is not public, so this is the task in my own
words.)* You are given `n` nodes labelled `0 .. n-1` and a list of undirected
edges. Return how many **connected components** the graph has. Isolated nodes
each count as their own component.

Worth asking: can edges repeat, and can an edge be a self-loop? Both are
harmless for DSU (they simply produce a union that returns `False`), but a
DFS-with-visited implementation has to be careful not to double-count. Also
ask whether the graph is static — if edges arrive **online** and the count is
queried between insertions, DSU stops being a stylistic choice and becomes the
only reasonable answer.
""",
        ),
        (
            "The insight",
            """
Do not traverse. Start with `n` components — every node alone — and merge:

```
components = n
for a, b in edges:
    if union(a, b): components -= 1
```

A successful `union` fuses two distinct sets into one, which is exactly one
fewer component. A `union` that returns `False` means the endpoints already
shared a root, so the edge is redundant and the count is untouched. There is
no visited array, no recursion, no stack-overflow risk on a 10⁵-node path.

The equivalence worth being able to state: **components = n − (number of
successful unions)**, and the number of successful unions is the size of any
spanning forest. That single identity is what makes Graph Valid Tree, Number
of Operations to Make Network Connected, and Kruskal's MST all the same
problem wearing different clothes.
""",
        ),
        (
            "Follow-ups",
            """
- **"Now edges are added one at a time and I ask for the count after each."**
  DSU answers in O(α(n)) per edge; a DFS re-run is O(n + e) per edge, so at
  e = 10⁵ that is 10¹⁰ operations against roughly 10⁵. This is the version the
  interviewer actually wants to hear about.
- **"Now edges are also *removed*."** DSU has no undo. Say so — the honest
  answers are offline dynamic connectivity (a segment tree over the time axis
  with a rollback DSU, which needs union-by-rank *without* path compression) or
  a link-cut tree. Do not pretend a plain DSU handles deletion.
- **"Return the size of the largest component."** Track a `size[]` array in the
  DSU and keep a running max inside `union`; both stay O(α(n)).
- **Weighted variants** — Accounts Merge and Evaluate Division are this loop
  with a `dict` DSU keyed on strings instead of an array keyed on integers.
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
        """False means they already shared a root — the edge is redundant."""
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


def count_components(n: int, edges: list[list[int]]) -> int:
    dsu = UnionFind(n)
    components = n

    for a, b in edges:
        if dsu.union(a, b):
            components -= 1  # two sets became one

    return components


CASES = [
    ((5, [[0, 1], [1, 2], [3, 4]]), 2),
    ((5, [[0, 1], [1, 2], [2, 3], [3, 4]]), 1),
    ((1, []), 1),
    ((0, []), 0),
    ((4, []), 4),
    ((4, [[0, 1], [1, 0], [2, 3]]), 2),  # duplicate edge must not double-count
    ((3, [[0, 0], [1, 1]]), 3),  # self-loops connect nothing
]


def solve(n: int, edges: list[list[int]]) -> int:
    return count_components(n, edges)
