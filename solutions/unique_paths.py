"""Unique Paths — LeetCode 62."""

from __future__ import annotations

from math import comb

META = {
    "pattern": "dp-grid-knapsack",
    "insight": "You arrive at a cell from above or from the left, and those two sets of paths are disjoint — so the counts add.",
    "time": "O(m · n), or O(min(m, n)) with the closed form",
    "space": "O(n), or O(1)",
    "sections": [
        (
            "What it asks",
            """
Count the paths from the top-left to the bottom-right of an `m × n` grid,
moving only right or down.

Ask: only right and down (yes); are there obstacles (that is Unique Paths II);
is the grid at least 1×1.
""",
        ),
        (
            "State",
            """
> `dp[r][c]` = the number of ways to reach cell `(r, c)`.

The recurrence is `dp[r][c] = dp[r-1][c] + dp[r][c-1]`.

**Why it is a plain sum:** the paths arriving from above and the paths
arriving from the left are **disjoint** sets — a path cannot do both on its
final step. Saying that one sentence is what turns the recurrence from a guess
into an argument.
""",
        ),
        (
            "Base cases",
            """
The first row and the first column are all 1: there is exactly one path along
each edge, because you can only move in one direction.
""",
        ),
        (
            "The fold",
            """
Rolling one row at a time drops the space from O(m·n) to O(n).

The update `dp[c] += dp[c-1]` reads as **"from above, plus from the left"** —
because when it executes, `dp[c]` still holds the *previous* row's value while
`dp[c-1]` already holds the *current* row's. That aliasing is deliberate, and
worth explaining rather than leaving as a magic line.
""",
        ),
        (
            "The closed form",
            """
Finish strongly. This is combinatorics: you make exactly `(m-1) + (n-1)` moves
and choose which of them are downward. So the answer is

```
C(m + n - 2, m - 1)
```

in O(min(m, n)) time and O(1) space.

Give the DP first — it is what they asked for and it generalises to the
obstacle version — then offer this. Leading with the formula skips the part
being assessed.
""",
        ),
        (
            "Follow-ups",
            """
- **Unique Paths II**, with obstacles. Set blocked cells to 0. The catch: the
  first row and column base case now **stops at the first obstacle**, since
  nothing beyond it is reachable along the edge. That is what breaks naive
  adaptations.
- **Minimum Path Sum** — same traversal, `min` instead of `+`.
- **Unique Paths III** — visit every non-obstacle cell exactly once, which is
  [backtracking](../../patterns/backtracking/), not DP.
""",
        ),
    ],
}


def unique_paths(rows: int, cols: int) -> int:
    dp = [1] * cols  # first row: one path along the top edge

    for _ in range(1, rows):
        for c in range(1, cols):
            # dp[c] still holds the row above; dp[c-1] holds this row.
            dp[c] += dp[c - 1]

    return dp[-1]


def unique_paths_closed_form(rows: int, cols: int) -> int:
    """The combinatorial answer: choose which of the moves go down."""
    return comb(rows + cols - 2, rows - 1)


CASES = [
    ((3, 7), 28),
    ((3, 2), 3),
    ((7, 3), 28),
    ((1, 1), 1),
    ((1, 10), 1),
    ((10, 1), 1),
    ((23, 12), 193536720),
]


def solve(rows: int, cols: int) -> int:
    return unique_paths(rows, cols)


def check() -> None:
    for args, expected in CASES:
        assert unique_paths(*args) == expected
        # The DP and the closed form must agree.
        assert unique_paths_closed_form(*args) == expected
