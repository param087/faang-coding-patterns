"""Maximal Square — LeetCode 221."""

from __future__ import annotations

META = {
    "pattern": "dp-grid-knapsack",
    "insight": "A square of side k can end at a cell only if its up, left and diagonal neighbours all end squares of side k−1.",
    "time": "O(m · n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Find the largest square of `'1'` cells in a binary matrix and return its
**area**, not its side. The matrix holds characters, not integers — a small
detail that has broken plenty of submissions.

Ask: square or rectangle? (Square. The rectangle version is a different
problem and a much harder one.) Area or side? Must the square be axis-aligned
(yes)? Is the matrix guaranteed non-empty (LeetCode says yes, but guard it).
""",
        ),
        (
            "Brute force, and the number",
            """
For every cell, try every side length and verify the square:

```
O(m · n · min(m, n)²)
```

Verifying one `k × k` candidate costs `k²`; summed over every cell and every
side that fits in a 300 × 300 all-ones matrix that is **8·10¹⁰ operations**.

The obvious repair is a 2-D prefix sum so each candidate is checked in O(1),
which brings it to 9·10⁴ cells × 300 sides = 2.7·10⁷ — genuinely fast enough,
and worth naming as the fallback if the DP recurrence will not come. But it
costs O(mn) extra space and generalises to nothing, so treat it as a stepping
stone rather than the answer.
""",
        ),
        (
            "The insight",
            """
> `dp[r][c]` = the side of the largest all-ones square whose **bottom-right
> corner** is `(r, c)`.

Anchoring at a corner is the move. "Largest square somewhere in this
sub-rectangle" is not a state you can extend in O(1); "largest square ending
*here*" is.

```
dp[r][c] = min(dp[r-1][c], dp[r][c-1], dp[r-1][c-1]) + 1   if cell is '1'
dp[r][c] = 0                                               otherwise
```

Track the running maximum side as you fill, and square it at the end.
""",
        ),
        (
            "Why three neighbours, and why min",
            """
This is the part to say out loud, because the formula is unmemorable and the
argument is not.

A square of side `k` ending at `(r, c)` is exactly a square of side `k-1`
ending at each of `(r-1, c)`, `(r, c-1)` and `(r-1, c-1)`, plus the cell
itself. Each neighbour certifies one part: **up** certifies the columns above,
**left** certifies the rows to the left, and the **diagonal** certifies the
interior that neither of the other two can see.

Drop the diagonal and you get a wrong answer on

```
1 1 1
1 0 1
1 1 1
```

where `min(up, left) + 1` reports a 2×2 square at the bottom-right — a square
that contains the hole at the centre. The correct answer is 1. That grid is
the single test worth writing down before you code.

`min` rather than `max` because the square is limited by its **weakest**
corner: a side of `k` requires all three to reach `k-1`, so the smallest of
them is the binding constraint.
""",
        ),
        (
            "Dry run",
            """
```
1 0 1 0 0
1 0 1 1 1
1 1 1 1 1
1 0 0 1 0
```

The `dp` sides, with a zero-padded first row and column:

```
1 0 1 0 0
1 0 1 1 1
1 1 1 2 2
1 0 0 1 0
```

The `2` at row 2, column 3 is the moment it works: up is 1, left is 1,
diagonal is 1 → side 2. Its neighbour to the right also reaches 2. Nothing
reaches 3, because row 3 mostly breaks. Maximum side 2 → area **4**.

Note the padding. Writing `dp` one row and one column larger than the matrix
removes every `r == 0 or c == 0` branch, which is where the off-by-ones live.
""",
        ),
        (
            "Follow-ups",
            """
- **Count Square Submatrices with All Ones** (LC 1277) — the *same* `dp`,
  summed rather than maximised, because a cell with `dp = k` is the corner of
  exactly `k` squares. If you can state that in one line you have shown you
  understand the state rather than the formula.
- **Maximal Rectangle** (LC 85) — not this DP. It is a histogram per row plus
  Largest Rectangle in Histogram; the `min` of three neighbours has no
  rectangle analogue.
- **Return the coordinates**, not the area — keep the argmax cell; the square
  spans `(r - side + 1, c - side + 1)` to `(r, c)`.
- **Streaming rows** — the rolling two-row version below already does this in
  O(n) memory, so you can answer for a matrix that never fits in RAM.
""",
        ),
    ],
}


def maximal_square(matrix: list[list[str]]) -> int:
    if not matrix or not matrix[0]:
        return 0

    cols = len(matrix[0])
    previous = [0] * (cols + 1)  # padded: index c holds column c - 1
    best_side = 0

    for row in matrix:
        current = [0] * (cols + 1)
        for c in range(1, cols + 1):
            if row[c - 1] == "1":
                # Up, left and diagonal — the weakest one binds.
                current[c] = min(previous[c], previous[c - 1], current[c - 1]) + 1
                best_side = max(best_side, current[c])
        previous = current

    return best_side * best_side


CASES = [
    ((
        [
            ["1", "0", "1", "0", "0"],
            ["1", "0", "1", "1", "1"],
            ["1", "1", "1", "1", "1"],
            ["1", "0", "0", "1", "0"],
        ],
    ), 4),
    (([["1", "1", "1"], ["1", "0", "1"], ["1", "1", "1"]],), 1),  # min of two says 4
    (([["0", "1"], ["1", "0"]],), 1),
    (([["1", "1"], ["1", "1"]],), 4),
    (([["0"]],), 0),
    (([["1"]],), 1),
    (([["1", "1", "1"], ["1", "1", "1"], ["1", "1", "1"]],), 9),
    (([],), 0),
]


def solve(matrix: list[list[str]]) -> int:
    return maximal_square(matrix)
