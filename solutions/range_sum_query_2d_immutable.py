"""Range Sum Query 2D - Immutable — LeetCode 304."""

from __future__ import annotations

META = {
    "pattern": "prefix-sums",
    "symbol": "NumMatrix",
    "insight": "One padded prefix grid plus inclusion-exclusion: any rectangle is four table lookups, whatever its size.",
    "time": "O(mn) to build, O(1) per query",
    "space": "O(mn)",
    "sections": [
        (
            "What it asks",
            """
Build a structure over a fixed matrix that answers `sumRegion(row1, col1, row2,
col2)` — the sum of the axis-aligned rectangle, inclusive on all four sides —
for many queries. The matrix never changes.

Ask: **how many queries?** LeetCode says up to 10⁴ calls on a 200 × 200 grid,
and those two numbers are the entire design brief. Confirm the corners are
inclusive and that `(row1, col1)` is guaranteed to be the top-left — if it is
not, normalise with `min`/`max` before you index, or you will silently return
the wrong sign.
""",
        ),
        (
            "Two tempting precomputes, and the numbers that rule them out",
            """
**Sum the rectangle per query.** O(mn) each: 4 × 10⁴ cells × 10⁴ queries =
**4 × 10⁸** additions. Too slow, and the whole point of the class is that
construction is allowed to be expensive.

**Precompute every rectangle.** There are `C(201, 2)² = 20100² ≈ 4 × 10⁸`
rectangles in a 200 × 200 grid. As 4-byte integers that is 1.6 GB. The idea
dies on memory, not time — say which resource it blows, because "too slow"
would be the wrong diagnosis here.

**Prefix sums per row.** Genuinely reasonable: O(m) per query, so 200 × 10⁴ =
2 × 10⁶ operations. It passes. Offer it as the intermediate step, then note that
the same idea applied on the second axis removes the last factor of `m`.
""",
        ),
        (
            "The insight",
            """
Define `P[r][c]` as the sum of the whole rectangle from the origin to just
before row `r` and column `c` — the 2-D analogue of the exclusive prefix array.

Building it is inclusion-exclusion, because the block above and the block to
the left overlap in the corner that must be subtracted back out:

```
P[r+1][c+1] = M[r][c] + P[r][c+1] + P[r+1][c] - P[r][c]
```

Querying is the same identity in reverse: take the big rectangle from the
origin, cut off the strip above, cut off the strip to the left, and add back
the corner you removed twice:

```
sum = P[r2+1][c2+1] - P[r1][c2+1] - P[r2+1][c1] + P[r1][c1]
```

Four lookups and three additions, independent of the rectangle's size. The
signs `+ - - +` are the same in both formulas, which is the mnemonic worth
carrying.
""",
        ),
        (
            "Pad the grid, do not guard the edges",
            """
Make `P` an `(m + 1) × (n + 1)` grid whose first row and first column are zero.
This is not tidiness; it is the difference between a correct answer and twenty
minutes of index debugging.

Without the padding, `row1 == 0` and `col1 == 0` each need their own branch, and
the two of them together need a third — four cases in the query and four more
in the build, all of which look plausible and one of which will be wrong. With
the padding, the empty strips read as the structural zeros in row 0 and column
0 and every query is the same four lookups.

The cost of the same habit elsewhere in this pattern: the leading `0` in the
1-D prefix array, and the `{0: -1}` seed in the hash-map variants. Same idea
each time — represent the empty prefix explicitly rather than testing for it.

The other thing that bites: **shifting only one index**. The query uses
`r2 + 1` and `c2 + 1` for the bottom-right but raw `r1` and `c1` for the
top-left, precisely because the top-left corner is exclusive. Writing `r1 - 1`
by reflex — the 1-D `left - 1` habit — reintroduces the boundary case you just
removed.
""",
        ),
        (
            "Dry run",
            """
The 5 × 5 grid from the problem:

```
3 0 1 4 2
5 6 3 2 1
1 2 0 1 5
4 1 0 1 7
1 0 3 0 5
```

Its padded prefix grid `P` (6 × 6; row 0 and column 0 are zero):

```
 0  0  0  0  0  0
 0  3  3  4  8 10
 0  8 14 18 24 27
 0  9 17 21 28 36
 0 13 22 26 34 49
 0 14 23 30 38 58
```

`sumRegion(2, 1, 4, 3)` — rows 2–4, columns 1–3:

```
P[5][4] - P[2][4] - P[5][1] + P[2][1]
   38   -   24    -   14    +    8    = 8
```

Check by hand: `(2+0+1) + (1+0+1) + (0+3+0) = 8`. The `+ P[2][1]` term is the
corner that both subtractions removed; drop it and you get `0`.
""",
        ),
        (
            "Follow-ups",
            """
- **Mutable version (308)** — a 2-D Fenwick tree, O(log m · log n) for both
  update and query. Recognising that the immutable trick cannot survive updates
  is the point; a single cell change invalidates O(mn) prefix entries.
- **Number of Submatrices That Sum to Target (1074)** — fix a pair of rows,
  collapse each column to a single number, and the problem becomes 1-D Subarray
  Sum Equals K. O(m² n).
- **Max Sum of Rectangle No Larger Than K (363)** — same row-pair collapse, but
  the inner 1-D problem needs an ordered set of prefix sums.
- **Overflow** — in Java a 200 × 200 grid of values up to 10⁵ sums to 4 × 10⁹,
  which overflows `int`. Use `long` for the prefix grid.
- **Sparse matrices** — if almost every cell is zero, an O(mn) grid is wasteful;
  store the non-zero cells sorted and answer with a 2-D range query structure.
""",
        ),
    ],
}


class NumMatrix:
    def __init__(self, matrix: list[list[int]]) -> None:
        rows = len(matrix)
        cols = len(matrix[0]) if matrix else 0

        # Padded by one row and one column of zeros: prefix[r][c] is the sum of
        # everything strictly above row r and strictly left of column c.
        self.prefix = [[0] * (cols + 1) for _ in range(rows + 1)]

        for r in range(rows):
            for c in range(cols):
                self.prefix[r + 1][c + 1] = (
                    matrix[r][c]
                    + self.prefix[r][c + 1]
                    + self.prefix[r + 1][c]
                    - self.prefix[r][c]  # the corner counted twice
                )

    def sum_region(self, row1: int, col1: int, row2: int, col2: int) -> int:
        # Bottom-right is shifted by one; top-left is not, because it is exclusive.
        return (
            self.prefix[row2 + 1][col2 + 1]
            - self.prefix[row1][col2 + 1]
            - self.prefix[row2 + 1][col1]
            + self.prefix[row1][col1]  # add back what both cuts removed
        )


CASES: list[tuple[tuple, object]] = []


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
    assert matrix.sum_region(1, 1, 2, 2) == 11
    assert matrix.sum_region(1, 2, 2, 4) == 12

    # The padded row and column are what make these need no special case.
    assert matrix.sum_region(0, 0, 0, 0) == 3
    assert matrix.sum_region(0, 0, 4, 4) == 58
    assert matrix.sum_region(0, 0, 0, 4) == 10  # first row only
    assert matrix.sum_region(0, 0, 4, 0) == 14  # first column only
    assert matrix.sum_region(4, 4, 4, 4) == 5  # bottom-right single cell

    # Cross-check every rectangle against a brute-force sum.
    for r1 in range(5):
        for c1 in range(5):
            for r2 in range(r1, 5):
                for c2 in range(c1, 5):
                    expected = sum(
                        grid[r][c] for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)
                    )
                    assert matrix.sum_region(r1, c1, r2, c2) == expected

    # Negatives, where a wrong sign in the inclusion-exclusion shows up loudly.
    signed = [[-1, 2, -3], [4, -5, 6], [-7, 8, -9]]
    negative = NumMatrix(signed)
    assert negative.sum_region(0, 0, 2, 2) == -5
    assert negative.sum_region(1, 1, 2, 2) == 0
    assert negative.sum_region(0, 1, 1, 2) == 0
    assert negative.sum_region(2, 0, 2, 0) == -7

    # Degenerate shapes must still build.
    single = NumMatrix([[42]])
    assert single.sum_region(0, 0, 0, 0) == 42

    row = NumMatrix([[1, 2, 3, 4]])
    assert row.sum_region(0, 1, 0, 3) == 9

    column = NumMatrix([[1], [2], [3]])
    assert column.sum_region(1, 0, 2, 0) == 5

    empty = NumMatrix([])
    assert empty.prefix == [[0]]
