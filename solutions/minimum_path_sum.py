"""Minimum Path Sum — LeetCode 64."""

from __future__ import annotations

META = {
    "pattern": "dp-grid-knapsack",
    "insight": "The sample grid is itself the greedy counterexample: taking the cheaper first step commits you to 9 when 7 was available.",
    "time": "O(m · n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Walk top-left to bottom-right, right and down only, minimising the sum of the
cells you land on. Both endpoints count.

Ask: **are the values non-negative?** LeetCode says yes (0 to 200), and that
matters — with negative cells and four-directional movement this stops being
DP and becomes shortest path with a priority queue.
""",
        ),
        (
            "The insight",
            """
> `dp[r][c]` = the cheapest way to reach `(r, c)`.

`dp[r][c] = grid[r][c] + min(dp[r-1][c], dp[r][c-1])`. Identical traversal to
Unique Paths with `min` in place of `+`; the disjointness argument that
justified the sum here justifies the min, because the last step came from
exactly one of the two.

**Lead with why greedy fails**, using the problem's own sample:

```
1 3 1
1 5 1
4 2 1
```

Greedy from the corner takes the 1 below rather than the 3 to the right, and
is then stuck paying 5 or 4: total **9**. The optimum goes *through* the 3 —
`1 → 3 → 1 → 1 → 1` = **7**. One cheap step bought an expensive commitment,
which is precisely the exchange argument greedy needs and does not have here.

Rolling one row keeps it at O(n) space: when `dp[c] = row[c] + min(dp[c],
dp[c-1])` executes, `dp[c]` is still the row above and `dp[c-1]` is already
this row.
""",
        ),
        (
            "In place, and the boundaries",
            """
You can write the DP straight into `grid` for O(1) extra space. Say so, then
**ask before doing it** — mutating the caller's input is a real cost and some
interviewers are testing whether you notice. (For that reason `solve` here
copies nothing but never writes to `grid` either.)

The boundaries are what break rushed implementations:

- **Row 0** has no cell above; **column 0** has no cell to the left. Handle
  them as prefix sums, not with `min` against a missing neighbour.
- Seeding a sentinel `0` outside the grid is wrong for a *minimising* DP — the
  fake 0 always wins the `min`. If you want sentinels they must be `+∞`, with
  `dp[0][0]` seeded separately.
- A 1×n or n×1 grid is entirely boundary, so it is the fastest test of whether
  you got that right.
""",
        ),
    ],
}


def min_path_sum(grid: list[list[int]]) -> int:
    if not grid or not grid[0]:
        return 0

    cols = len(grid[0])
    dp = [0] * cols

    for r, row in enumerate(grid):
        for c in range(cols):
            if r == 0 and c == 0:
                dp[0] = row[0]
            elif r == 0:
                dp[c] = dp[c - 1] + row[c]  # top edge: prefix sum
            elif c == 0:
                dp[0] += row[0]  # left edge: prefix sum
            else:
                # dp[c] is still the row above; dp[c - 1] is already this row.
                dp[c] = row[c] + min(dp[c], dp[c - 1])

    return dp[-1]


CASES = [
    (([[1, 3, 1], [1, 5, 1], [4, 2, 1]],), 7),  # greedy says 9
    (([[1, 2, 3], [4, 5, 6]],), 12),
    (([[5]],), 5),
    (([[1, 2, 3, 4]],), 10),  # single row: all boundary
    (([[1], [2], [3]],), 6),  # single column: all boundary
    (([[0, 0], [0, 0]],), 0),
    (([[1, 100, 100], [1, 100, 100], [1, 1, 1]],), 5),
    (([],), 0),
]


def solve(grid: list[list[int]]) -> int:
    return min_path_sum(grid)
