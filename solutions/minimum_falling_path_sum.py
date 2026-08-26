"""Minimum Falling Path Sum — LeetCode 931."""

from __future__ import annotations

META = {
    "pattern": "dp-grid-knapsack",
    "insight": "A cell's best falling path is its own value plus the cheapest of the three cells directly above it, so one row of state suffices.",
    "time": "O(n²)",
    "space": "O(n) with a rolling row",
    "sections": [
        (
            "What it asks",
            """
Fall from any cell in the top row to any cell in the bottom row of an `n × n`
matrix. From `(r, c)` the next step is `(r+1, c-1)`, `(r+1, c)` or `(r+1, c+1)`.
Return the minimum sum of the cells visited.

Ask whether values can be **negative** — they can (LeetCode allows −100…100),
and that single fact kills every greedy and every early-exit pruning idea.
""",
        ),
        (
            "The insight",
            """
> `dp[c]` = the cheapest falling path that **ends** at column `c` of the row
> just processed.

Then `dp'[c] = row[c] + min(dp[c-1], dp[c], dp[c+1])`, clamped at the edges, and
the answer is `min(dp)` over the final row.

Two details make the argument, and stating them is what separates a derivation
from a memorised recurrence:

- The three predecessors are the **only** ways to reach `(r, c)`, so taking a
  `min` over them loses nothing.
- The cost of the prefix and the cost of the suffix are independent given the
  column you pass through — that is the optimal-substructure claim, and it holds
  because the move rule only ever looks at the current column.

Each row overwrites the previous one, so the table collapses to a single array
of length `n`. Build the new row into a fresh list: updating in place corrupts
`dp[c-1]` for the neighbour that still needs the old value.
""",
        ),
        (
            "Why row-wise greedy fails",
            """
The tempting shortcut is "take the smallest cell in each row". Adjacency makes
that illegal:

```
  1 100 100
100 100   1
  1 100 100
```

Greedy reads off `1 + 1 + 1 = 3`, but columns 0 and 2 are not adjacent, so that
path does not exist. The real answer is **102**.

The other classic slip is caching only the column of the current best rather
than the best *per column*. With negative values a path that is behind at row
`r` routinely wins by row `n-1`, which is exactly why all `n` columns must be
carried forward.
""",
        ),
    ],
}


def min_falling_path_sum(matrix: list[list[int]]) -> int:
    if not matrix or not matrix[0]:
        return 0

    cols = len(matrix[0])
    best = list(matrix[0])  # a copy: never write through to the caller's data

    for row in matrix[1:]:
        # A fresh row — updating in place would clobber the left neighbour.
        best = [
            row[c] + min(best[max(0, c - 1) : min(cols, c + 2)])
            for c in range(cols)
        ]

    return min(best)


CASES = [
    (([[2, 1, 3], [6, 5, 4], [7, 8, 9]],), 13),
    (([[-19, 57], [-40, -5]],), -59),
    (([[-48]],), -48),
    (([[1, 100, 100], [100, 100, 1], [1, 100, 100]],), 102),  # greedy says 3
    (([[1, 2, 3], [4, 5, 6], [7, 8, 9]],), 12),
    (([[5, 3], [2, 1]],), 4),
    (([[-1, -2, -3], [-4, -5, -6], [-7, -8, -9]],), -18),
    (([],), 0),
]


def solve(matrix: list[list[int]]) -> int:
    return min_falling_path_sum([row[:] for row in matrix])
