"""Number of Provinces — LeetCode 547."""

from __future__ import annotations

META = {
    "pattern": "union-find",
    "insight": "Count components without ever building a graph: merge every 1 in the upper triangle, then count roots.",
    "time": "O(n² · α(n))",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Given an `n × n` symmetric matrix where `isConnected[i][j] == 1` means cities
`i` and `j` are directly linked, return how many **connected components**
(provinces) there are.

Worth asking: is the matrix guaranteed symmetric with a 1-diagonal (yes on
LeetCode) — because that lets you scan only `j > i` and halve the work. Also
ask whether `n` can be large enough that the adjacency *matrix* is the
bottleneck: at n = 200 it is 40,000 cells, trivial; at n = 10⁵ the input could
not be given this way at all, which is the hint that an edge list version of
this problem is a different question.
""",
        ),
        (
            "The insight",
            """
This is the canonical "how many components" question, and both DFS and DSU are
correct. Reach for DSU when you want to *say something*: the union-find answer
is `n` minus the number of successful unions, so the count falls out of the
merges rather than needing a second traversal.

```
provinces = n
for i, for j > i, if isConnected[i][j] and union(i, j): provinces -= 1
```

Every successful `union` merges two components into one, so it reduces the
count by exactly one. A union that returns `False` means the pair was already
connected — a redundant edge — and changes nothing.

Scanning only `j > i` matters: the matrix is symmetric, so the lower triangle
repeats every edge, and the diagonal `isConnected[i][i] == 1` would be a
self-loop. Neither breaks correctness (both are just failing unions) but both
double the work for nothing.
""",
        ),
        (
            "Edge cases",
            """
- **`n = 1`** → one province. The loop body never runs and the initial count
  is already right.
- **The identity matrix** (no city linked to any other) → `n` provinces. This
  is the case that catches an implementation which starts the counter at 0 and
  tries to increment on merges.
- **All ones** → one province, and `n - 1` successful unions out of the
  `n(n-1)/2` pairs examined. Watch that your DSU does not degrade to O(n) per
  find here: without union-by-rank (or by size), merging in scan order builds a
  path, and path compression alone still keeps it near-linear but rank makes
  the bound airtight.
- **Counting roots at the end instead** — `sum(1 for i in range(n) if find(i) == i)`
  — is equally valid and costs one extra pass. Pick one and be consistent; a
  hybrid that decrements *and* recounts is where off-by-ones live.
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
        """False means they already shared a root — a redundant edge."""
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


def find_circle_num(is_connected: list[list[int]]) -> int:
    n = len(is_connected)
    dsu = UnionFind(n)
    provinces = n

    for i in range(n):
        for j in range(i + 1, n):  # symmetric, so skip the lower triangle
            if is_connected[i][j] and dsu.union(i, j):
                provinces -= 1  # every real merge kills one component

    return provinces


CASES = [
    (([[1, 1, 0], [1, 1, 0], [0, 0, 1]],), 2),
    (([[1, 0, 0], [0, 1, 0], [0, 0, 1]],), 3),
    (([[1]],), 1),
    (([[1, 1, 1], [1, 1, 1], [1, 1, 1]],), 1),
    (([[1, 1, 0, 0], [1, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 1]],), 2),
    (([[1, 0, 0, 1], [0, 1, 1, 0], [0, 1, 1, 0], [1, 0, 0, 1]],), 2),
]


def solve(is_connected: list[list[int]]) -> int:
    return find_circle_num(is_connected)
