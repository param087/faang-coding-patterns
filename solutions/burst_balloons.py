"""Burst Balloons — LeetCode 312."""

from __future__ import annotations

META = {
    "pattern": "dp-advanced",
    "insight": "Choosing which balloon to burst first breaks the array in two halves that still interact; choosing which one bursts last does not.",
    "time": "O(n³)",
    "space": "O(n²)",
    "sections": [
        (
            "What it asks",
            """
Balloons in a row carry values. Bursting balloon `i` pays
`left * nums[i] * right`, where `left` and `right` are its **current**
neighbours — the ones that survive, not the original ones — with a virtual 1
off each end. Burst all of them in some order and maximise the total.

The whole difficulty is in "current". Every burst rewires the neighbours of
everything around it, so the payout of a balloon depends on the entire history
of what has been popped so far.

Worth confirming: values are non-negative (LeetCode says 0–100), the array can
have zeros, and you must burst **every** balloon rather than choosing a subset.
""",
        ),
        (
            "Brute force, and why it fails",
            """
Try every order: `n!`. At n = 12 that is **479,001,600** orderings, and
LeetCode allows n up to 300.

Memoising on "which balloons are still alive" is better — the remaining set
determines the future — but that is `2ⁿ` states. At n = 25 that is 33 million
states each with 25 moves, and at n = 300 the state count has 90 digits.
Subsets are the wrong state.
""",
        ),
        (
            "The insight",
            """
The natural recursion is "pick the balloon to burst **first**". It does not
work: after bursting `i`, the left part and the right part are *not*
independent, because when the left part is finally emptied its last balloon's
right neighbour comes from the right part. The subproblems talk to each other,
so they cannot be solved separately.

Turn it around: **pick the balloon that bursts last** in a range.

If `last` is the final balloon burst strictly between boundaries `left` and
`right`, then at the moment it pops, everything between them is already gone,
so its neighbours are exactly `left` and `right` — known, fixed, independent of
order. And every other balloon in `(left, last)` was burst while `last` was
still standing, so it never saw anything beyond `last`. Same on the other side.
Now the two halves really are independent:

```
dp[left][right] = max over last in (left, right) of
    dp[left][last] + nums[left]*nums[last]*nums[right] + dp[last][right]
```

`dp[left][right]` = best coins from bursting everything **strictly between**
`left` and `right`, with both boundaries still alive. Pad the array with a 1 at
each end so the outermost range needs no special case, and the answer is
`dp[0][n+1]`.

That is why this is an interval DP and not a subset DP: the surviving set is
always a contiguous range plus its two intact walls, so O(n²) states suffice.
""",
        ),
        (
            "The details that decide it",
            """
**Open interval, not closed.** `dp[left][right]` excludes both endpoints. Get
this wrong and you will double-count the boundary balloons or lose them. The
base case is `right - left < 2` → 0, which the loop gets for free by starting
lengths at 2.

**Iterate by span length, not by index.** `dp[left][right]` reads
`dp[left][last]` and `dp[last][right]`, both strictly shorter spans. A plain
nested `for left / for right` loop reads cells that have not been filled yet
and quietly returns a too-small answer. Either loop `length` outward, or loop
`left` downward and `right` upward, or write it as a memoised recursion where
the order takes care of itself.

**The padding is 1, not 0.** Multiplying by a 0 wall would zero out every
edge burst. The problem's "treat it as a balloon with value 1" is doing real
work.

**Zeros inside the array are fine** and need no filtering. A zero balloon pays
nothing whenever it pops, and because you must burst everything, deleting it
up front changes nothing — but it also buys nothing, so leave it.
""",
        ),
        (
            "Dry run",
            """
`[3, 1, 5, 8]`, padded to `[1, 3, 1, 5, 8, 1]`.

Short spans first:

- `dp[1][3]` — burst the lone `1` between 3 and 5 → `3·1·5 = 15`.
- `dp[1][4]` — balloons `1, 5` between the walls 3 and 8. Best `last` is **5**:
  `dp[1][3] = 15`, plus `3·5·8 = 120` → **135**.
- `dp[0][4]` — balloons `3, 1, 5` between 1 and 8. Best `last` is **3**:
  `0 + 1·3·8 = 24`, plus `dp[1][4] = 135` → **159**.
- `dp[0][5]` — the whole thing. Best `last` is **8**: `dp[0][4] = 159`, plus
  `1·8·1 = 8` → **167**.

Unwinding the "last" choices gives the burst order 1, 5, 3, 8:
`15 + 120 + 24 + 8 = 167`.

Contrast the obvious greedy — always pop the current smallest — which on the
same input burst 1, 3, 5, 8 for `15 + 15 + 40 + 8 = 78`. Less than half.
""",
        ),
        (
            "Follow-ups",
            """
- **Minimum Cost to Merge Stones (1000)** and **Remove Boxes (546)** are the
  same family: an interval DP whose state needs one extra dimension because
  the cost of merging depends on something beyond the range. Remove Boxes in
  particular is the version where `dp[left][right]` alone is insufficient and
  you carry "how many equal boxes are glued to the left end".
- **Matrix Chain Multiplication** is this recurrence with `+` instead of the
  last-burst trick — split on the *first* operator, which works there precisely
  because matrix products do not rewire their neighbours.
- **Print the burst order** — store the winning `last` per cell and unwind it,
  exactly as in the dry run.
- **"Can you do better than O(n³)?"** Not known for the general case. The
  Knuth–Yao speedup does not apply because the cost term is not monotone in the
  right way, so O(n³) — 2.7·10⁷ operations at n = 300 — is the target.
""",
        ),
    ],
}


def max_coins(nums: list[int]) -> int:
    balloons = [1, *nums, 1]  # virtual walls so edge bursts need no branch
    n = len(balloons)
    # dp[left][right] = best coins from bursting everything STRICTLY between.
    dp = [[0] * n for _ in range(n)]

    for length in range(2, n):  # shortest spans first: the recurrence reads them
        for left in range(n - length):
            right = left + length
            best = 0
            for last in range(left + 1, right):
                # `last` pops when only the walls remain, so its neighbours are known.
                coins = (
                    dp[left][last]
                    + balloons[left] * balloons[last] * balloons[right]
                    + dp[last][right]
                )
                best = max(best, coins)
            dp[left][right] = best

    return dp[0][n - 1]


CASES = [
    (([3, 1, 5, 8],), 167),
    (([1, 5],), 10),
    (([5],), 5),
    (([],), 0),
    (([1, 1, 1],), 3),
    (([2, 4, 0, 3],), 33),
    (([9, 76, 64, 21],), 116718),
    (([7, 9, 8, 0, 7, 1, 3],), 1141),
]


def solve(nums: list[int]) -> int:
    return max_coins(nums)
