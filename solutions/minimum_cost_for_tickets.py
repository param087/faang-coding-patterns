"""Minimum Cost For Tickets — LeetCode 983."""

from __future__ import annotations

META = {
    "pattern": "dp-advanced",
    "insight": "Index the DP by calendar day, not by travel day, and a pass bought today is just a jump back 1, 7 or 30 slots.",
    "time": "O(D) where D is the last travel day (≤ 365)",
    "space": "O(D)",
    "sections": [
        (
            "What it asks",
            """
You travel on a given sorted set of days within a year. Three passes are on
sale: 1-day, 7-day and 30-day, priced `costs[0..2]`. A pass bought on day `d`
covers `d` through `d + 6` (or `d + 29`) **consecutive calendar days**, whether
or not you travel on them. Minimise the spend.

The clarification that matters: a 7-day pass is seven *calendar* days, not
seven *travel* days. Everyone who mis-reads that writes an off-by-a-lot
solution. Also confirm passes may overlap and may be bought on a day you do not
travel — both are allowed, and neither ever helps, which is why the DP can
restrict purchases to travel days.

Greedy does not survive. "Buy a 30-day pass whenever the next 30 days contain
more than `costs[2] / costs[0]` travel days" fails as soon as the cheap regions
interlock; the choice on day 1 depends on a pattern 30 days out.
""",
        ),
        (
            "The insight",
            """
Let `dp[d]` be the minimum cost to cover **all travel on or before calendar day
`d`**. Walk `d` from 1 to the last travel day:

```
dp[d] = dp[d-1]                                  if you do not travel on d
dp[d] = min(dp[d-1]  + costs[0],
            dp[d-7]  + costs[1],
            dp[d-30] + costs[2])                 if you do
```

Read the travel branch backwards: *if the pass covering day `d` is the 7-day
one, it was bought no later than `d` and no earlier than `d-6`, so everything
up to `d-7` had to be paid for separately.* Buying it as late as possible is
never worse, so `dp[d-7]` is the right predecessor and no inner loop over the
purchase date is needed.

The non-travel branch is what makes it linear and correct at once: it lets a
pass bought earlier "coast" over idle days without special handling, and it is
why `dp[d-7]` refers to a real, already-computed value even when day `d-7` is
not a travel day.

Clamp the lookbacks with `max(0, d - 7)`, and keep `dp[0] = 0`. Cost is O(365)
in the worst case — small enough that the sparse alternative below is a
follow-up, not the expected answer.
""",
        ),
        (
            "Edge cases and the sparse variant",
            """
- **`days` empty** → 0. Nothing to cover, buy nothing.
- **A single travel day** → `min(costs)`, which the recurrence produces because
  all three branches read `dp[0] = 0`. If the 30-day pass is the cheapest of
  the three (the constraints permit it), the answer is `costs[2]` — a
  reasonable-looking `costs[0]` shortcut is wrong.
- **Off-by-one**: 7 days means `d-7`, not `d-6`. Sanity-check with days 1…7 and
  a 7-day pass: buying on day 1 must cover through day 7, so `dp[7]` reads
  `dp[0]`. If your code reads `dp[1]` you are charging twice for day 1.
- **Do not index by position in `days`.** `dp[i] = min(dp[i-1] + costs[0], …)`
  over travel *indices* cannot express "the 7-day pass covers however many
  travel days happen to fall in the window" without a search, and that search
  is where people get it wrong.
- **Follow-up — the horizon is huge** (days spread over 10 years, or arbitrary
  timestamps). Then O(D) is unacceptable and you keep the DP over the `n`
  travel days only, using binary search: `dp[i] = min(dp[i-1] + costs[0],
  dp[j7] + costs[1], dp[j30] + costs[2])` where `j7` is the first index with
  `days[j] > days[i] - 7`, found by `bisect`. O(n log n), or O(n) with two
  sliding pointers since `days` is sorted.
- **Follow-up — which passes did you buy?** Store the winning branch per day
  and unwind; the answer is a list of (buy date, pass type).
""",
        ),
    ],
}


def mincost_tickets(days: list[int], costs: list[int]) -> int:
    if not days:
        return 0

    travel = set(days)
    horizon = days[-1]  # `days` is sorted; nothing past the last trip matters
    dp = [0] * (horizon + 1)  # dp[d] = cheapest cover for all travel <= d

    for day in range(1, horizon + 1):
        if day not in travel:
            dp[day] = dp[day - 1]  # coast: an idle day costs nothing extra
            continue
        # Whichever pass covers `day`, buy it as late as legal.
        dp[day] = min(
            dp[day - 1] + costs[0],
            dp[max(0, day - 7)] + costs[1],
            dp[max(0, day - 30)] + costs[2],
        )

    return dp[horizon]


CASES = [
    (([1, 4, 6, 7, 8, 20], [2, 7, 15]), 11),
    (([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 30, 31], [2, 7, 15]), 17),
    (([1, 4, 6, 7, 8, 20], [7, 2, 15]), 6),  # weekly cheaper than daily
    (([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29], [3, 10, 25]), 25),
    (([1, 2], [2, 7, 15]), 4),
    (([1], [2, 7, 15]), 2),
    (([365], [15, 8, 2]), 2),  # the 30-day pass is the cheapest single buy
    (([], [2, 7, 15]), 0),
]


def solve(days: list[int], costs: list[int]) -> int:
    return mincost_tickets(days, costs)
