"""Range Sum Query 2D - Mutable — LeetCode 308."""

from __future__ import annotations

META = {
    "pattern": "segment-tree",
    "symbol": "NumMatrix",
    "insight": "A 2-D Fenwick is a Fenwick of Fenwicks: the same low-bit walk on rows, with each row node holding a whole tree over columns.",
    "time": "O(m·n·log m·log n) build, O(log m · log n) per update and per query",
    "space": "O(m·n)",
    "sections": [
        (
            "What it asks",
            """
This one is premium, so the statement is not public — in my own words: design a
`NumMatrix` over an `m × n` integer grid supporting two operations that both
happen often — `update(row, col, value)` assigning a single cell, and
`sumRegion(row1, col1, row2, col2)` returning the sum of an axis-aligned
sub-rectangle, corners inclusive.

Ask the ratio of updates to queries before writing anything. It decides the
whole answer:

- **Queries only** → 2-D prefix sums, O(1) per query. That is problem 304, and
  reaching for it here is the mistake this problem is built to catch.
- **Updates only** → the raw grid, O(1) per update.
- **Both frequent** → neither works: the prefix grid costs O(m·n) to repair
  after one cell changes, and the raw grid costs O(m·n) per region sum. At
  200 × 200 with 10⁴ mixed operations that is 4 × 10⁸ cell touches.
""",
        ),
        (
            "The insight",
            """
A sum is **invertible**, so a rectangle sum is four prefix rectangles combined
by inclusion–exclusion:

```
sum(r1..r2, c1..c2) = P(r2,c2) - P(r1-1,c2) - P(r2,c1-1) + P(r1-1,c1-1)
```

That reduces the problem to "prefix sum to (r, c), with cells changing" — which
is exactly what a Fenwick tree gives in one dimension. Lift it: `tree[i][j]`
covers the rows `i & -i` block crossed with the columns `j & -j` block, so the
update walk is a nested `while` on both axes and the prefix walk is the same
nesting with the low bit subtracted instead of added.

Both walks touch log m × log n nodes. At 200 × 200 that is roughly 8 × 8 = 64
cells per operation instead of 40 000.

Say out loud why a **segment tree** is not the choice here: you would need one
for min, max or gcd, where there is no inverse and the four-corner subtraction
is meaningless. Picking the cheaper structure on purpose is the signal.
""",
        ),
        (
            "The two details that decide it",
            """
**`update` is an assignment, but a Fenwick only adds.** Keep a shadow copy of
the raw grid, compute `value - shadow[row][col]`, add *that*, then write the
shadow. Skip the shadow and repeated updates to one cell accumulate silently —
the first update looks right, so this survives a hand-trace and dies on the
judge.

**Index from 1 on both axes.** `i -= i & -i` never terminates at `i = 0`, so
every entry point adds 1 and every prefix call is written against the
one-indexed tree. Mixing conventions between the row loop and the column loop
is the other reliable way to lose twenty minutes here.

Two smaller ones worth naming: an empty matrix (`[]` or `[[]]`) must not crash
the constructor, and building by calling `update` on every cell is
O(m·n·log m·log n) — fine at these limits, but if the constructor were hot you
would build in O(m·n) with the in-place linear Fenwick construction instead.
""",
        ),
    ],
}


class NumMatrix:
    def __init__(self, matrix: list[list[int]]) -> None:
        self.rows = len(matrix)
        self.cols = len(matrix[0]) if self.rows else 0
        # Shadow copy: the tree stores deltas, so we need the raw values back.
        self.values = [row[:] for row in matrix]
        self.tree = [[0] * (self.cols + 1) for _ in range(self.rows + 1)]

        for r in range(self.rows):
            for c in range(self.cols):
                self._add(r, c, matrix[r][c])

    def _add(self, row: int, col: int, delta: int) -> None:
        i = row + 1  # one-indexed on both axes
        while i <= self.rows:
            j = col + 1
            while j <= self.cols:
                self.tree[i][j] += delta
                j += j & -j
            i += i & -i

    def _prefix(self, row: int, col: int) -> int:
        """Sum of the rectangle (0, 0)..(row, col), inclusive; -1 means empty."""
        total = 0
        i = row + 1
        while i > 0:
            j = col + 1
            while j > 0:
                total += self.tree[i][j]
                j -= j & -j
            i -= i & -i
        return total

    def update(self, row: int, col: int, value: int) -> None:
        delta = value - self.values[row][col]  # a delta, not an assignment
        self.values[row][col] = value
        self._add(row, col, delta)

    def sum_region(self, row1: int, col1: int, row2: int, col2: int) -> int:
        # Inclusion-exclusion over four prefix rectangles.
        return (
            self._prefix(row2, col2)
            - self._prefix(row1 - 1, col2)
            - self._prefix(row2, col1 - 1)
            + self._prefix(row1 - 1, col1 - 1)
        )


def check() -> None:
    grid = [
        [3, 0, 1, 4, 2],
        [5, 6, 3, 2, 1],
        [1, 2, 0, 1, 5],
        [4, 1, 0, 1, 7],
        [1, 0, 3, 0, 5],
    ]
    matrix = NumMatrix(grid)
    assert matrix.sum_region(2, 1, 4, 3) == 8
    matrix.update(3, 2, 2)
    assert matrix.sum_region(2, 1, 4, 3) == 10

    # Repeated updates to one cell must replace, not accumulate.
    matrix.update(3, 2, 100)
    matrix.update(3, 2, 0)
    assert matrix.sum_region(3, 2, 3, 2) == 0
    assert matrix.sum_region(2, 1, 4, 3) == 8

    single = NumMatrix([[7]])
    assert single.sum_region(0, 0, 0, 0) == 7
    single.update(0, 0, -7)
    assert single.sum_region(0, 0, 0, 0) == -7

    # Empty inputs must not blow up the constructor.
    assert NumMatrix([]).rows == 0
    assert NumMatrix([[]]).cols == 0

    # Negatives, non-square, and every rectangle cross-checked by brute force.
    raw = [[4, -1, 9], [0, 3, -7], [2, 2, 2], [-5, 6, 0]]
    checked = NumMatrix(raw)
    checked.update(1, 2, 5)
    raw[1][2] = 5
    checked.update(3, 0, -1)
    raw[3][0] = -1
    for r1 in range(len(raw)):
        for c1 in range(len(raw[0])):
            for r2 in range(r1, len(raw)):
                for c2 in range(c1, len(raw[0])):
                    expected = sum(
                        raw[r][c] for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)
                    )
                    assert checked.sum_region(r1, c1, r2, c2) == expected
