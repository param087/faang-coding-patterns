"""Profitable Schemes — LeetCode 879."""

from __future__ import annotations

META = {
    "pattern": "dp-grid-knapsack",
    "insight": "Profit beyond minProfit is indistinguishable from minProfit, so clamp it — that bounds a dimension the inputs do not.",
    "time": "O(len(group) · n · minProfit)",
    "space": "O(n · minProfit)",
    "sections": [
        (
            "What it asks",
            """
Each crime `i` needs `group[i]` members and yields `profit[i]`. A member who
joins a crime cannot join another. Count the subsets of crimes whose total
headcount is **at most** `n` and total profit is **at least** `minProfit`,
modulo 1e9+7.

Ask two things. First: is a member consumed by one crime only (yes — that makes
headcount a knapsack capacity rather than a per-crime check). Second: does the
empty scheme count when `minProfit == 0`? It does, and that is exactly the base
case the table needs.
""",
        ),
        (
            "The insight",
            """
Two constraints, so two dimensions. Headcount is naturally bounded by `n ≤ 100`.
Profit is not: `Σ profit` can reach 10 000 while `minProfit ≤ 100`.

The unlock is that **profit above `minProfit` is not worth distinguishing**.
A scheme earning 4 000 and one earning 100 are equally acceptable and will stay
equally acceptable no matter what you add later. So clamp:

> `dp[j][k]` = number of schemes using **at most** `j` members whose profit is
> **at least** `k`, where `k` is capped at `minProfit`.

Base case `dp[j][0] = 1` for every `j`: the empty scheme already earns "at least
0". Then per crime `(g, p)`, in 0/1-knapsack order,

```
dp[j][k] += dp[j - g][max(0, k - p)]
```

`max(0, k - p)` *is* the clamp, read backwards: to end at `k` you only needed
`k - p` before, and anything below zero collapses to the "already satisfied"
row. The answer is `dp[n][minProfit]`.

At the limits that is 100 × 100 × 100 = one million updates.
""",
        ),
        (
            "Pitfall: the loop order and the direction of both axes",
            """
Two independent reversals, and getting either wrong changes the answer silently:

- **Members must descend** (`j` from `n` down to `g`). Ascending reuses the same
  crime several times within one pass — unbounded knapsack, wildly over-counting.
- **Profit must also descend** here, because `dp[j][k]` and `dp[j-g][k-p]` live
  in different `j` rows but the `k` axis is still being rewritten in place. With
  `g == 0` crimes (allowed: `group[i]` can be 0) the two rows coincide and an
  ascending `k` loop double-counts.

The other classic slip is defining `dp[j]` as "**exactly** `j` members" and then
returning `dp[n][minProfit]` instead of summing over `j ≤ n`. "At most" in the
state definition is what makes the last line a single lookup.
""",
        ),
    ],
}

MOD = 10**9 + 7


def profitable_schemes(n: int, min_profit: int, group: list[int], profit: list[int]) -> int:
    # dp[j][k]: schemes with at most j members and profit at least k (k capped).
    dp = [[0] * (min_profit + 1) for _ in range(n + 1)]
    for members in range(n + 1):
        dp[members][0] = 1  # the empty scheme already clears a bar of 0

    for need, earns in zip(group, profit, strict=True):
        for members in range(n, need - 1, -1):  # descending: each crime once
            row, prev = dp[members], dp[members - need]
            for bar in range(min_profit, -1, -1):
                row[bar] = (row[bar] + prev[max(0, bar - earns)]) % MOD

    return dp[n][min_profit]


CASES = [
    ((5, 3, [2, 2], [2, 3]), 2),
    ((10, 5, [2, 3, 5], [6, 7, 8]), 7),
    ((1, 1, [2], [3]), 0),  # the only paying crime needs more members than exist
    ((5, 0, [2, 2], [2, 3]), 4),  # minProfit 0: the empty scheme counts too
    ((1, 0, [1, 1], [1, 1]), 3),
    ((2, 2, [1, 1], [1, 1]), 1),
    ((10, 5, [2, 3, 5], [0, 0, 0]), 0),
    ((100, 10, [2, 5, 36, 2, 5], [3, 61, 52, 39, 6]), 28),
]


def solve(n: int, min_profit: int, group: list[int], profit: list[int]) -> int:
    return profitable_schemes(n, min_profit, list(group), list(profit))
