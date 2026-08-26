"""Matchsticks to Square — LeetCode 473."""

from __future__ import annotations

META = {
    "pattern": "backtracking",
    "insight": "Assign sticks to four buckets rather than enumerating subsets, place the longest first, and never try two buckets holding the same amount.",
    "time": "O(4ⁿ) worst case, but the three prunes hold n ≤ 15 to milliseconds",
    "space": "O(n) recursion depth",
    "sections": [
        (
            "What it asks",
            """
Given stick lengths, decide whether **all** of them can be arranged into a
square — four groups of equal sum, every stick used, no breaking and no
overlapping.

The constraint that shapes the answer: `n ≤ 15`. That says exponential is
expected and that the interviewer wants to see pruning, not a polynomial trick.
It also hints at the bitmask-DP alternative over 2ⁿ = 32768 subsets.

Ask whether lengths are positive. LeetCode guarantees it, and the answer below
relies on it — with zeros or negatives the "longest stick first" and
"stick > side" arguments both collapse.
""",
        ),
        (
            "The insight",
            """
The wrong first framing is "pick a subset summing to `side`, remove it, repeat".
That is 2ⁿ subsets per side and re-does work across sides. Turn it inside out:
walk the **sticks** and assign each to one of **four buckets**. One decision per
stick, four options, and the recursion depth is `n`.

Raw, that is 4¹⁵ ≈ 10⁹ — too slow. Three prunes collapse it:

1. **Reject early.** `sum % 4 != 0`, fewer than four sticks, or any single stick
   longer than `side` — all impossible, and all O(n) to detect.
2. **Longest stick first.** Sort descending. Big sticks have few legal homes, so
   failures surface at depth 1 or 2 rather than depth 14. This is the single
   biggest win; without it the same input can go from milliseconds to minutes.
3. **Skip equal buckets.** If two buckets currently hold the same amount, they
   are interchangeable — putting this stick in either leads to isomorphic
   subtrees. Track the fill levels already tried at this node in a small set and
   skip repeats. On the trivial input `[1,1,1,1]` that alone cuts the tree by 4×;
   on skewed inputs it is far more.

The empty-bucket case is a special case of prune 3 and matters most: all empty
buckets have level `0`, so a fresh stick is only ever placed into the *first*
empty bucket.
""",
        ),
        (
            "The input that breaks greedy",
            """
`[4,3,2,3,5,2,1]` — sum 20, `side = 5`. First-fit descending puts `5` in bucket
one, `4` in bucket two, `3` in bucket three, `3` in bucket four, then `2` fits
nowhere. Greedy answers **false**; the truth is `[5], [4,1], [3,2], [3,2]` →
**true**. That input exists to punish anyone who skips the backtracking.

The other input to keep in your pocket is `[7,7,7,7,1,1,1,1,4,4]`: sum 40, so
`side = 10`, and every stick individually fits. Each `7` needs exactly `3` more,
and the only way to make `3` is `1+1+1` — there is one such triple and four
sevens, so the answer is **false**. Divisibility and per-stick feasibility both
pass; only the search settles it.

**Follow-up.** For `n ≤ 15`, memoise on the used-stick bitmask: state is
`(mask, current bucket fill)`, and since the fill is determined by
`sum(mask) % side` the state is just the mask — 32768 states, O(2ⁿ · n). That
converts the worst case from 4ⁿ to 2ⁿ · n and generalises directly to
[Partition to K Equal Sum Subsets](../partition-to-k-equal-sum-subsets/).
""",
        ),
    ],
}


def makesquare(matchsticks: list[int]) -> bool:
    total = sum(matchsticks)
    if len(matchsticks) < 4 or total % 4:
        return False

    side = total // 4
    sticks = sorted(matchsticks, reverse=True)  # longest first: fail fast
    if sticks[0] > side:
        return False

    sides = [0] * 4

    def place(i: int) -> bool:
        if i == len(sticks):
            return True

        tried: set[int] = set()  # bucket fill levels already attempted here
        for j in range(4):
            if sides[j] in tried or sides[j] + sticks[i] > side:
                continue
            tried.add(sides[j])  # equal buckets are interchangeable

            sides[j] += sticks[i]  # choose
            if place(i + 1):  # explore
                return True
            sides[j] -= sticks[i]  # un-choose

        return False

    return place(0)


CASES = [
    (([1, 1, 2, 2, 2],), True),
    (([3, 3, 3, 3, 4],), False),  # sum 16, but the 4 leaves a 3 stranded
    (([4, 3, 2, 3, 5, 2, 1],), True),  # first-fit descending says False here
    (([7, 7, 7, 7, 1, 1, 1, 1, 4, 4],), False),  # divisible, fits, still impossible
    (([2, 2, 2, 6],), False),  # sum 12, but 6 > side 3
    (([10, 6, 5, 5, 5, 3, 3, 3, 2, 2, 2, 2],), True),
    (([5],), False),  # fewer than four sticks
    (([],), False),
]


def solve(matchsticks: list[int]) -> bool:
    return makesquare(matchsticks)
