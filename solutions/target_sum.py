"""Target Sum — LeetCode 494."""

from __future__ import annotations

META = {
    "pattern": "dp-grid-knapsack",
    "insight": "Choosing which numbers get a minus sign is choosing a subset, and that subset must sum to (total + target) / 2.",
    "time": "O(n · total)",
    "space": "O(total)",
    "sections": [
        (
            "What it asks",
            """
Put a `+` or a `−` in front of every number — every number, none may be
skipped — and count the assignments whose sum is `target`.

Ask: **are the numbers non-negative?** LeetCode guarantees `0 ≤ nums[i] ≤
1000`, and the reduction below depends on it. Ask whether zeros can appear
(they can, and each one silently doubles the count). Ask whether `target` can
be negative (yes).
""",
        ),
        (
            "The insight",
            """
Let `P` be the numbers you make positive and `N` the ones you negate. Then

```
sum(P) - sum(N) = target
sum(P) + sum(N) = total
--------------------------------
     2 · sum(P) = total + target
```

so `sum(P) = (total + target) / 2`. The signs vanish: **count the subsets that
sum to a fixed value**, which is a 0/1 knapsack in one array.

> `dp[s]` = the number of subsets seen so far that sum to exactly `s`.

`dp[0] = 1` (the empty subset), and each number sweeps the array **downwards**
so it is used at most once. Sweeping upwards would count reuse and turn this
into the unbounded problem.

The reduction also hands you three O(1) rejections before any DP runs:
`total + target` negative, `total + target` odd, or `target > total`. A
sign-flipping search that misses the parity case will churn through 2²⁰
branches to return 0.
""",
        ),
        (
            "The zeros, and the other formulation",
            """
A zero can be `+0` or `−0`, so it doubles the answer while changing nothing.
The subset DP gets this right for free: with `num = 0` the inner loop does
`dp[s] += dp[s]`, doubling every entry. If you instead write the DP keyed on
"reachable sums" as a set, or start the loop at `range(subset, num, -1)`, you
lose exactly this case — `nums = [0,0,0,0,0], target = 0` should be **32**,
not 1.

The alternative formulation is a dictionary from running sum to count,
iterating the numbers and branching `s + num` / `s - num`. It is O(n · total)
too, handles negative inputs, and needs no parity check — a reasonable answer
when the interviewer relaxes the non-negativity constraint. The array version
is faster and is the one they are usually fishing for, because the reduction
is the insight being tested.
""",
        ),
    ],
}


def find_target_sum_ways(nums: list[int], target: int) -> int:
    total = sum(nums)
    doubled = total + target

    # Out of range, or the subset sum is not an integer.
    if doubled < 0 or doubled % 2 or doubled // 2 > total:
        return 0

    subset = doubled // 2
    dp = [0] * (subset + 1)
    dp[0] = 1  # the empty subset sums to zero

    for num in nums:
        # Downwards: each number joins at most one subset per entry.
        # For num == 0 this is dp[s] += dp[s], which doubles — correctly.
        for s in range(subset, num - 1, -1):
            dp[s] += dp[s - num]

    return dp[subset]


CASES = [
    (([1, 1, 1, 1, 1], 3), 5),
    (([1], 1), 1),
    (([1], 2), 0),  # target beyond the total
    (([0, 0, 0, 0, 0], 0), 32),  # every zero doubles the count
    (([1, 0], 1), 2),
    (([2], 1), 0),  # parity rejection
    (([100], -100), 1),  # negative target
    (([1, 2, 3], 0), 2),
]


def solve(nums: list[int], target: int) -> int:
    return find_target_sum_ways(nums, target)
