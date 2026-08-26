"""Min Cost Climbing Stairs — LeetCode 746."""

from __future__ import annotations

META = {
    "pattern": "dp-1d",
    "insight": "You pay to leave a step, not to land on it, and the destination is one past the last index.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Each index of `cost` charges you when you **step off** it, moving one or two
places forward. You may start at index 0 or index 1 for free. Reach the top —
the position just past the last index — for the least total.

Ask the two questions that decide the code: is the top index `n-1` or `n`
(it is `n`), and is the starting step free (yes, both of them).
""",
        ),
        (
            "The insight",
            """
Same take-or-skip shape as Climbing Stairs, but now the edges are weighted:

> `dp[i]` = cheapest way to **stand on** position `i`.

```
dp[i] = min(dp[i-1] + cost[i-1], dp[i-2] + cost[i-2])
dp[0] = dp[1] = 0
```

The cost belongs to the step you are leaving, so it attaches to the transition
rather than to the state. Answer is `dp[n]`.

Only two entries are read, so fold the array into two variables — O(1) space.
Do the fold in the room after writing the array version; it is a free point.
""",
        ),
        (
            "The off-by-one that decides it",
            """
Two ways to lose this one, and neither is an algorithm failure:

1. **Returning `dp[n-1]`.** You would be paying to reach the last step and
   then never leaving it. The answer is `dp[n]` — one past the end.
2. **Charging on arrival.** Writing `dp[i] = cost[i] + min(dp[i-1], dp[i-2])`
   makes the top cost `cost[n-1]` extra, because `cost[n]` does not exist.

Sanity check on `[10, 15, 20]`: start at index 1, pay 15, land on index 3 —
the top. **15**, not 30. If your code says 30 you are charging on arrival.

Both `n = 0` and `n = 1` return 0: you are already at or one step from the
top, and starting is free.
""",
        ),
    ],
}


def min_cost_climbing_stairs(cost: list[int]) -> int:
    # cheapest way to stand on position i-2 and i-1; both start free
    two_back, one_back = 0, 0

    for i in range(2, len(cost) + 1):
        two_back, one_back = one_back, min(one_back + cost[i - 1], two_back + cost[i - 2])

    return one_back  # dp[n] — one past the last index


CASES = [
    (([10, 15, 20],), 15),
    (([1, 100, 1, 1, 1, 100, 1, 1, 100, 1],), 6),
    (([1, 2, 3, 4, 5, 6, 7, 8, 9, 10],), 25),
    (([0, 0, 0, 0],), 0),
    (([10, 15],), 10),
    (([7],), 0),
    (([],), 0),
]


def solve(cost: list[int]) -> int:
    return min_cost_climbing_stairs(cost)
