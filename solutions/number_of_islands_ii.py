"""Number of Islands II — LeetCode 305."""

from __future__ import annotations

META = {
    "pattern": "union-find",
    "insight": "Land only appears, never disappears, so islands can only merge — count up on each new cell, down on each union that succeeds.",
    "time": "O(k · α(k)) for k additions — independent of the grid size",
    "space": "O(k)",
    "sections": [
        (
            "What it asks",
            """
LeetCode 305 is premium, so the statement is not public — described here in my
own words. You are given an `m × n` grid that starts as all water, and a list
of positions that are turned into land one at a time. After each addition,
report how many islands exist (four-directional connectivity).

Ask two things. **Can a position repeat?** The judge's data does contain
repeats and they must not change the count — that single detail is most of the
question. And **how large is the grid relative to the number of additions?**
`m·n` can be 10⁹ while `k` is 10⁴, which decides the data structure.
""",
        ),
        (
            "The insight",
            """
The naive answer is "BFS the grid after every addition": O(k · m · n). At
k = 10⁴ on a 1000×1000 grid that is 10¹⁰ cell visits. Worse, it is the wrong
*shape* of answer — the grid is only ever gaining land, and re-deriving the
whole picture each time throws that away.

Because water never returns, islands can only ever **merge**. So maintain a
running count:

- adding a new land cell: `count += 1` (it is its own island for a moment);
- for each of the four neighbours that is already land, `union()`. Every union
  that actually merges two distinct roots does `count -= 1`.

A cell dropped into the middle of four separate islands does one `+1` and four
`-1`s, and lands on the right answer without anybody counting anything.

Use a **dict-keyed DSU** rather than an `m·n` array. Only cells that have been
added ever exist, so memory is O(k) and a 10⁹-cell grid costs nothing.
""",
        ),
        (
            "The duplicate-position trap",
            """
If the same position appears twice and you blindly do `count += 1`, the count
is permanently one too high and every subsequent answer is wrong. The failure
is invisible on the sample and only shows up deep in a hidden test.

Guard at the point of insertion — `add()` returning `False` means "already
land, this addition is a no-op" — and return the current count unchanged. Do
not try to detect it later.

Two related edges worth stating out loud:

- an empty `positions` list returns `[]`, not `[0]`;
- neighbours must be bounds-checked *and* checked for being land already; a
  dict DSU makes the second test just `neighbour in parent`.

Follow-up an interviewer will reach for: **"now support removing land."** DSU
does not support deletion, so the honest answer is offline reversal — process
the removals backwards as additions — or a link-cut tree if they insist on
online.
""",
        ),
    ],
}


class UnionFind:
    """Sparse DSU: only cells that have been added exist as nodes."""

    def __init__(self) -> None:
        self.parent: dict[int, int] = {}
        self.rank: dict[int, int] = {}
        self.count = 0

    def add(self, x: int) -> bool:
        """False means x was already land — the duplicate-position guard."""
        if x in self.parent:
            return False
        self.parent[x] = x
        self.rank[x] = 0
        self.count += 1
        return True

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
        self.count -= 1  # two islands became one
        return True


def num_islands2(m: int, n: int, positions: list[list[int]]) -> list[int]:
    dsu = UnionFind()
    answers: list[int] = []

    for row, col in positions:
        cell = row * n + col
        if dsu.add(cell):  # skip the whole body on a repeated position
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                r, c = row + dr, col + dc
                if 0 <= r < m and 0 <= c < n and r * n + c in dsu.parent:
                    dsu.union(cell, r * n + c)
        answers.append(dsu.count)

    return answers


CASES = [
    ((3, 3, [[0, 0], [0, 1], [1, 2], [2, 1]]), [1, 1, 2, 3]),
    # The centre cell merges four separate islands in one addition.
    ((3, 3, [[0, 1], [1, 0], [1, 2], [2, 1], [1, 1]]), [1, 2, 3, 4, 1]),
    # Repeated positions must not bump the count.
    ((3, 3, [[0, 0], [0, 0], [0, 1], [0, 1]]), [1, 1, 1, 1]),
    # One cell bridging two islands.
    ((1, 3, [[0, 0], [0, 2], [0, 1]]), [1, 2, 1]),
    ((1, 1, [[0, 0]]), [1]),
    ((3, 3, []), []),
    # Diagonal neighbours are not connected.
    ((2, 2, [[0, 0], [1, 1]]), [1, 2]),
]


def solve(m: int, n: int, positions: list[list[int]]) -> list[int]:
    return num_islands2(m, n, positions)
