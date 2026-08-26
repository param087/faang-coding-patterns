"""Cherry Pickup II — LeetCode 1463."""

from __future__ import annotations

META = {
    "pattern": "dp-grid-knapsack",
    "insight": "The robots descend in lockstep, so one shared row index plus two columns is the whole state — nine joint moves per step.",
    "time": "O(rows · cols²) — nine transitions per state",
    "space": "O(cols²)",
    "sections": [
        (
            "What it asks",
            """
Two robots start at the top-left and top-right of a grid. Each moves down one
row per step, shifting at most one column left or right. Collect the maximum
total cherries; a cell shared by both robots on the same step counts **once**.

Ask: do both robots move on **every** step (yes — they descend together, which
is the fact that makes a single time index work), and may they cross or occupy
the same cell (yes, they just do not double-count).
""",
        ),
        (
            "The insight",
            """
The trap is treating this as two independent path problems: run the single-robot
DP twice, blank out the first path, run it again. That is wrong, and there is a
two-line counterexample —

```
0 0 0
0 7 0
```

Independently each robot's best path takes the 7, so the naive sum reports
**14** when the real answer is **7**. The robots interact, so they have to be
optimised jointly.

They also move in lockstep, so there is no need to index time separately per
robot:

> `dp[c1][c2]` = the most cherries collectable once robot 1 sits at column `c1`
> and robot 2 at column `c2` of the current row.

Each step, both robots pick one of three shifts, so there are **nine** joint
transitions from every state. The gain at the destination is
`grid[r][n1] + grid[r][n2]`, minus one copy when `n1 == n2`.

`cols² · 9` transitions per row, `rows` rows. At the 70 × 70 limit that is under
3 million operations.
""",
        ),
        (
            "Pitfall: the unreachable sentinel",
            """
Not every `(c1, c2)` pair is reachable — the robots start at opposite corners
and can drift only one column per row, so after `r` rows robot 1 cannot be past
column `r`. Initialising the table to `0` instead of a negative sentinel lets
those phantom states compete in the `max`, and on a grid with a single large
cluster in one corner you will get a value that no real pair of paths achieves.

Cherries are non-negative, so `-1` is a safe "unreachable" marker: any genuine
state is `≥ 0`.

Also seed only `dp[0][cols - 1]`, and handle `cols == 1` — both robots start on
the same cell, so the top-left value is counted once, not twice.
""",
        ),
    ],
}

UNREACHABLE = -1


def cherry_pickup(grid: list[list[int]]) -> int:
    rows, cols = len(grid), len(grid[0])

    # dp[c1][c2]: best total with robot 1 at c1 and robot 2 at c2 in this row.
    dp = [[UNREACHABLE] * cols for _ in range(cols)]
    last = cols - 1
    dp[0][last] = grid[0][0] + (grid[0][last] if last != 0 else 0)

    for r in range(1, rows):
        nxt = [[UNREACHABLE] * cols for _ in range(cols)]
        for c1 in range(cols):
            for c2 in range(cols):
                best_so_far = dp[c1][c2]
                if best_so_far == UNREACHABLE:
                    continue  # never let a phantom state feed the max
                for d1 in (-1, 0, 1):
                    n1 = c1 + d1
                    if not 0 <= n1 < cols:
                        continue
                    for d2 in (-1, 0, 1):
                        n2 = c2 + d2
                        if not 0 <= n2 < cols:
                            continue
                        # A shared cell pays out once.
                        gain = grid[r][n1] + (grid[r][n2] if n1 != n2 else 0)
                        if best_so_far + gain > nxt[n1][n2]:
                            nxt[n1][n2] = best_so_far + gain
        dp = nxt

    return max(max(row) for row in dp)


CASES = [
    (([[3, 1, 1], [2, 5, 1], [1, 5, 5], [2, 1, 1]],), 24),
    (
        (
            [
                [1, 0, 0, 0, 0, 0, 1],
                [2, 0, 0, 0, 0, 3, 0],
                [2, 0, 9, 0, 0, 0, 0],
                [0, 3, 0, 5, 4, 0, 0],
                [1, 0, 2, 3, 0, 0, 6],
            ],
        ),
        28,
    ),
    (([[0, 0, 0], [0, 7, 0]],), 7),  # the naive "two independent paths" says 14
    (([[1]],), 1),  # one column: both robots share the start cell
    (([[1, 1]],), 2),
    (([[5, 5], [5, 5]],), 20),
    (([[1, 0, 1], [0, 5, 0], [3, 0, 3]],), 13),
    (([[0, 0, 0], [0, 0, 0]],), 0),
]


def solve(grid: list[list[int]]) -> int:
    return cherry_pickup([row[:] for row in grid])
