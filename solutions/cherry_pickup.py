"""Cherry Pickup — LeetCode 741."""

from __future__ import annotations

from functools import cache

META = {
    "pattern": "dp-grid-knapsack",
    "insight": "There and back is two downward walks; move both in lockstep so the shared step count collapses the state to three dimensions.",
    "time": "O(n³)",
    "space": "O(n³)",
    "sections": [
        (
            "What it asks",
            """
Walk an `n × n` grid from the top-left to the bottom-right moving right and
down, then walk back moving left and up. Cells hold 0, 1 (a cherry, picked up
and removed) or −1 (a thorn you cannot enter). Maximise cherries; if there is
no round trip at all, return 0.

Ask: is the grid square (yes, `n ≤ 50`); is a cherry consumed on the first
visit so the second walk gets nothing (yes, that is the whole difficulty); can
the start or the end be a thorn (yes — return 0).
""",
        ),
        (
            "The insight",
            """
Two reframings, both needed.

**One: the return trip is a forward trip.** A path from the corner back to the
origin moving left and up, reversed, is a path from the origin moving right
and down. So this is not "a walk and a walk back", it is **two walks from the
top-left to the bottom-right**, and the answer is the union of their cells.

**Two: run them in lockstep.** After `t` steps a walker at row `r` is at
column `t - r`, so a walker's position is one number given the clock. Track
both walkers at the same `t`:

> `dp[t][r1][r2]` = the most cherries two walkers can collect together after
> `t` steps, having reached rows `r1` and `r2`.

That is O(n³) states, 4 transitions each — both move right, both down, or one
each. When `r1 == r2` the walkers are on the same cell and the cherry counts
**once**; forgetting that is the standard bug and it inflates every answer.

The recursion below indexes on `(r1, c1, r2)` and derives `c2 = r1 + c1 - r2`,
which is the same state written differently. `-∞` marks a thorn or a
walked-off-grid cell so blocked branches can never win a `max`.
""",
        ),
        (
            "Why two greedy passes are wrong",
            """
The wrong first answer — and it is a very attractive one — is: run the ordinary
max-path DP once, zero out the cells it used, run it again, add the results.
It fails because the first path is chosen with no knowledge of what it leaves
behind. Have this 4×4 ready:

```
1 1 1 0
0 0 1 1
0 1 1 0
1 0 1 1
```

The best single path is worth **7** and it is unique: across the top, then
straight down the column of ones. Zero it out and the leftovers — one cherry
at `(1,3)`, one at `(2,1)`, one at `(3,0)` — cannot be strung onto a single
monotone path, so the second pass salvages 1 and greedy reports **8**.

The optimum is **9**, from a pair of paths worth 5 and 6. The best single path
appears in **neither** of them. That is the whole argument: the two walks have
to be chosen together, which is exactly why the state carries two positions
instead of one.

Two more details that decide the submission:

- **Return 0, not −∞**, when no valid round trip exists. `[[1,-1],[-1,1]]` has
  cherries and still returns 0.
- The lockstep formulation quietly proves the paths may **cross**; you never
  need to enforce non-crossing, because any two lockstep walks can be
  un-crossed without changing the multiset of cells visited at each step.
""",
        ),
    ],
}

BLOCKED = float("-inf")


def cherry_pickup(grid: list[list[int]]) -> int:
    n = len(grid)
    if n == 0 or grid[0][0] == -1 or grid[n - 1][n - 1] == -1:
        return 0

    @cache
    def best(r1: int, c1: int, r2: int) -> float:
        """Most cherries from here on, two walkers after r1 + c1 steps."""
        c2 = r1 + c1 - r2  # the clock fixes the second walker's column
        if r1 >= n or c1 >= n or r2 >= n or c2 >= n:
            return BLOCKED
        if grid[r1][c1] == -1 or grid[r2][c2] == -1:
            return BLOCKED

        gained = grid[r1][c1]
        if (r1, c1) != (r2, c2):
            gained += grid[r2][c2]  # same cell -> count the cherry once
        if r1 == n - 1 and c1 == n - 1:
            return gained

        # Each walker independently steps down or right.
        return gained + max(
            best(r1 + 1, c1, r2 + 1),
            best(r1 + 1, c1, r2),
            best(r1, c1 + 1, r2 + 1),
            best(r1, c1 + 1, r2),
        )

    total = best(0, 0, 0)
    best.cache_clear()  # the closure holds `grid`; do not keep it alive
    return int(total) if total > 0 else 0


CASES = [
    (([[0, 1, -1], [1, 0, -1], [1, 1, 1]],), 5),
    (([[1, 1, -1], [1, -1, 1], [-1, 1, 1]],), 0),  # no round trip exists
    (([[1]],), 1),
    (([[0]],), 0),
    (([[1, 1], [1, 1]],), 4),
    (([[1, -1], [-1, 1]],), 0),
    # Two greedy passes report 8 here; the optimum is 9.
    (([[1, 1, 1, 0], [0, 0, 1, 1], [0, 1, 1, 0], [1, 0, 1, 1]],), 9),
    # Every cherry is reachable by some pair of walks.
    (
        (
            [
                [1, 1, 1, 0, 0],
                [0, 0, 1, 0, 0],
                [0, 0, 1, 0, 0],
                [1, 0, 1, 0, 0],
                [1, 1, 1, 1, 1],
            ],
        ),
        12,
    ),
    # Two walks cannot cover the centre of a 3x3: 8, not 9.
    (([[1, 1, 1], [1, 1, 1], [1, 1, 1]],), 8),
]


def solve(grid: list[list[int]]) -> int:
    return cherry_pickup(grid)
