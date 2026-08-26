"""Dungeon Game — LeetCode 174."""

from __future__ import annotations

META = {
    "pattern": "dp-grid-knapsack",
    "insight": "Health-so-far and health-still-needed pull against each other, so run the DP backwards on the one that has optimal substructure.",
    "time": "O(m · n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
A grid of health deltas, walked right and down from the top-left to the
bottom-right. The knight dies the instant his health hits 0 — **including on
the first and last cells**. Return the smallest starting health that survives
the best possible route.

Ask: does the constraint apply on entry to the start cell too (yes, so the
answer is at least 1); can he be healed above his starting health (yes, there
is no cap); is movement really only right and down (yes — with four
directions this stops being a DP).
""",
        ),
        (
            "The insight",
            """
> `dp[r][c]` = the minimum health needed **on entering** `(r, c)` to survive
> from there to the end.

Read that backwards from the exit. Entering `(r, c)` you take
`dungeon[r][c]`, then you must still be holding whatever the cheaper of the
two onward cells demands:

```
need    = min(dp[r+1][c], dp[r][c+1]) - dungeon[r][c]
dp[r][c] = max(1, need)
```

The `max(1, ...)` is the entire problem. A room full of healing does not bank
credit you can spend on the way in — you must arrive alive regardless, so the
requirement floors at 1. Drop it and a big positive cell makes `need` zero or
negative, the requirement propagates as a fictitious surplus, and you
under-report the answer on exactly the grids that look easy.

Seed the two cells just past the exit with 1 and everything else outside with
+∞, so the sweep never needs a boundary branch.
""",
        ),
        (
            "Why the forward DP fails",
            """
The wrong first answer is to sweep forwards keeping the maximum health
reachable at each cell, then read off the deficit at the end. Being able to
say **why** that fails, in one sentence, is what the problem is testing: a
cell has two competing quantities — health banked so far, and health required
from here on — and neither alone is a sufficient state.

Concretely:

```
 0  -5   7
 0   0   1
-1  -2   2
```

At `(1, 2)` the route across the top arrives with health `0 − 5 + 7 + 1 = 3`;
the route through the middle arrives with `1`. A max-health forward sweep
keeps the top one and discards the other — and the top one dipped to −5, so
it reports a required stake of **6**. The discarded route never dips at all:
the answer is **1**.

Fixing the forward version means carrying *both* numbers and keeping a Pareto
frontier of (banked, required) pairs per cell. That is strictly more work than
turning the sweep around, which reduces the state to a single number because
"health needed from here" does not depend on how you arrived.

Two more traps: the answer is `max(1, ...)` even for a single all-positive
cell (`[[100]]` → 1), and the rolling one-row version has to be written
right-to-left, since `dp[c+1]` must still be the value from the row below.
""",
        ),
    ],
}


def calculate_minimum_hp(dungeon: list[list[int]]) -> int:
    if not dungeon or not dungeon[0]:
        return 1

    rows, cols = len(dungeon), len(dungeon[0])
    unreachable = 1 << 60
    dp = [[unreachable] * (cols + 1) for _ in range(rows + 1)]
    dp[rows][cols - 1] = dp[rows - 1][cols] = 1  # one step past the exit

    for r in range(rows - 1, -1, -1):
        for c in range(cols - 1, -1, -1):
            need = min(dp[r + 1][c], dp[r][c + 1]) - dungeon[r][c]
            dp[r][c] = max(1, need)  # never bank surplus health

    return dp[0][0]


CASES = [
    (([[-2, -3, 3], [-5, -10, 1], [10, 30, -5]],), 7),
    (([[1, -3, 3], [0, -2, 0], [-3, -3, -3]],), 3),
    (([[0, -5, 7], [0, 0, 1], [-1, -2, 2]],), 1),  # forward max-health says 6
    (([[0]],), 1),
    (([[-5]],), 6),
    (([[100]],), 1),  # healing does not lower the floor of 1
    (([[0, -3]],), 4),
    (([[0, -3], [-3, 0]],), 4),
    (([[-1, -1], [-1, -1]],), 4),
]


def solve(dungeon: list[list[int]]) -> int:
    return calculate_minimum_hp(dungeon)
