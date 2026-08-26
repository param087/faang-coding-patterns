"""Most Stones Removed with Same Row or Column — LeetCode 947."""

from __future__ import annotations

META = {
    "pattern": "union-find",
    "insight": "Every connected component can be stripped down to exactly one stone, so the answer is n minus the component count.",
    "time": "O(n · α(n))",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Stones sit on a plane. You may remove a stone if it shares a row **or** a
column with another stone that is still on the board. Return the maximum number
of removals.

Worth asking: coordinates go up to 10⁴ but there are at most 10³ stones, so the
grid is enormously sparse — never allocate it. Also confirm the removal rule is
evaluated against the *current* board, not the original: that is precisely what
makes the ordering question interesting.
""",
        ),
        (
            "The insight",
            """
Reframe: two stones sharing a row or a column are "connected", and connectivity
is transitive through intermediate stones. Within one connected component of
size `k` you can always remove `k - 1` stones — pick any spanning tree of the
component and delete leaves inward, so every stone you remove still has a
living neighbour at the moment you remove it. You can never remove the last
one, because it shares nothing with anything.

So the answer is `n - components`, and the greedy ordering question evaporates.
No simulation, no backtracking, no proof of exchange arguments — just count
components.

The implementation trick is not to union stone-to-stone (that would be O(n²)
pair comparisons). Instead remember, for each row and each column, the **first
stone seen there**, and union the current stone with those:

```
for i, (r, c) in enumerate(stones):
    if r in first_in_row: union(i, first_in_row[r])
    else: first_in_row[r] = i
    ... same for c
```

Transitivity does the rest: three stones in one row all end up merged even
though only two unions were performed. The common alternative — union row `r`
with `~c` in a single DSU keyed over rows and complemented columns — is the
same idea with a cuter encoding; this version is easier to say out loud.
""",
        ),
        (
            "Edge cases",
            """
- **No stones** → 0. A component count of 0 with `n = 0` gives `0 - 0`.
- **One stone** → 0. It shares nothing, so nothing is removable.
- **A diagonal** `[[0,0],[1,1],[2,2]]` → 0. Every stone is its own component;
  this is the case that catches anyone who assumed the answer is `n - 1`.
- **Duplicate coordinates** are not allowed by the constraints, but if they were
  they would union trivially and still be handled.
- The classic wrong first answer is to simulate removals greedily and hope the
  order does not matter. It genuinely does not matter — but only because of the
  spanning-tree argument above. If you cannot state that argument, the greedy
  is an unjustified guess; if you can, you do not need the greedy at all.
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
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


def remove_stones(stones: list[list[int]]) -> int:
    n = len(stones)
    dsu = UnionFind(n)
    components = n

    first_in_row: dict[int, int] = {}
    first_in_col: dict[int, int] = {}

    for i, (row, col) in enumerate(stones):
        # Union with one representative per line; transitivity covers the rest.
        for table, key in ((first_in_row, row), (first_in_col, col)):
            if key in table:
                if dsu.union(i, table[key]):
                    components -= 1
            else:
                table[key] = i

    return n - components  # every component keeps exactly one stone


CASES = [
    (([[0, 0], [0, 1], [1, 0], [1, 2], [2, 1], [2, 2]],), 5),
    (([[0, 0], [0, 2], [1, 1], [2, 0], [2, 2]],), 3),
    (([[0, 0]],), 0),
    (([],), 0),
    (([[0, 0], [1, 1], [2, 2]],), 0),
    (([[0, 1], [1, 0], [1, 1]],), 2),
    (([[0, 0], [0, 1], [1, 1], [1, 0]],), 3),
    (([[0, 0], [0, 1], [5, 5], [5, 9]],), 2),
]


def solve(stones: list[list[int]]) -> int:
    return remove_stones(stones)
