"""Unique Paths II — LeetCode 63."""

from __future__ import annotations

META = {
    "pattern": "dp-grid-knapsack",
    "insight": "An obstacle is not a cell to skip — it is a cell with zero ways in, and that one substitution turns Unique Paths into this.",
    "time": "O(m · n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Same grid walk as Unique Paths — right and down only, top-left to
bottom-right — except some cells are blocked. Count the paths that avoid them.

Ask two things. **Can the start or the finish itself be blocked?** (Yes, and
the answer is then 0 — this is the single most common miss.) **Is `1` the
obstacle or the free cell?** LeetCode uses `1` for the obstacle, which is the
opposite of most grid problems and reads wrong at a glance.
""",
        ),
        (
            "The insight",
            """
> `dp[r][c]` = the number of paths that reach `(r, c)`.

For a free cell the recurrence is unchanged, `dp[r][c] = dp[r-1][c] +
dp[r][c-1]`, because paths arriving from above and paths arriving from the
left are disjoint sets. For a blocked cell you do not skip it, you **write
zero into it**. A zero propagates on its own: everything downstream that would
have counted those paths now counts nothing.

That framing is what keeps the code to two lines. Trying instead to "route
around" obstacles with special cases is where people lose the problem.

Rolled to one row, `dp[c] += dp[c-1]` still reads as "from above, plus from
the left" — `dp[c]` holds the previous row when the statement runs, `dp[c-1]`
already holds this one.
""",
        ),
        (
            "Edge cases",
            """
- **Start blocked.** `dp[0]` is seeded to 1, then the very first cell's
  obstacle check overwrites it with 0 and everything stays 0. Free.
- **Finish blocked.** Same mechanism at the other end — the last write is a 0.
- **First row and column.** In the naive port people fill the edges with 1s
  before the loop, which is wrong: an obstacle in the top row makes every cell
  *beyond* it unreachable along that edge. The unified loop gets this right
  because `dp[c] += dp[c-1]` after a zero adds nothing.
- **1×1 grid.** `[[0]]` → 1, `[[1]]` → 0.
- **Counts get large.** LeetCode guarantees the *answer* fits in a 32-bit int,
  which quietly does not bound the table: block the entire last column of a
  100 × 100 grid and the answer is 0 while interior cells still count on the
  order of 10⁵⁸ paths. Python does not care; in Java or C++ say so before they
  ask, because `long` does not save you either — the guarantee is on the
  output, not the intermediates.
""",
        ),
    ],
}


def unique_paths_with_obstacles(grid: list[list[int]]) -> int:
    if not grid or not grid[0]:
        return 0

    cols = len(grid[0])
    dp = [0] * cols
    dp[0] = 1  # one way to stand on the start, until an obstacle says otherwise

    for row in grid:
        for c in range(cols):
            if row[c] == 1:
                dp[c] = 0  # blocked: zero ways in, and the zero propagates
            elif c > 0:
                dp[c] += dp[c - 1]  # from above (stale dp[c]) + from the left

    return dp[-1]


CASES = [
    (([[0, 0, 0], [0, 1, 0], [0, 0, 0]],), 2),
    (([[0, 1], [0, 0]],), 1),
    (([[0, 0, 0], [1, 1, 0], [0, 0, 0]],), 1),
    (([[1]],), 0),  # start blocked
    (([[0]],), 1),
    (([[0, 0], [0, 1]],), 0),  # finish blocked
    (([[0, 1, 0, 0]],), 0),  # edge base case must stop at the obstacle
    (([[0, 0], [1, 1], [0, 0]],), 0),
]


def solve(grid: list[list[int]]) -> int:
    return unique_paths_with_obstacles(grid)
