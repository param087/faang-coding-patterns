"""Partition Equal Subset Sum — LeetCode 416."""

from __future__ import annotations

META = {
    "pattern": "dp-1d",
    "insight": "Both halves sum to total/2, so the question is only whether some subset hits that one target — 0/1 knapsack on reachability.",
    "time": "O(n · S) where S is the total sum",
    "space": "O(S)",
    "sections": [
        (
            "What it asks",
            """
Split the array into two subsets with equal sums. Return whether it is
possible; you do not have to produce the split.

Ask whether values are positive (LeetCode says ≥ 1, and negatives would break
the "stop once you exceed the target" pruning entirely) and what the bounds
are — `n ≤ 200`, `nums[i] ≤ 100`, so `S ≤ 20000` and an O(n·S) table of
4·10⁶ booleans is completely fine. Quoting that number is how you justify a
pseudo-polynomial algorithm rather than apologising for it.
""",
        ),
        (
            "The insight",
            """
The second subset is whatever the first one leaves behind, so there is only
one degree of freedom. If the total is `S`, both halves must sum to `S/2`:

- **`S` odd → immediately false.** Free O(n) exit, and it is the first thing to
  say.
- otherwise the question is "is some subset summing to exactly `S/2`?" — 0/1
  subset-sum, each element usable at most once.

State: `reachable[t]` = can some subset of the elements seen so far sum to `t`.
Start with `reachable[0] = True` (the empty subset) and for each number turn on
every `t` where `t - num` was already reachable.

Values, not counts. You never need "how many subsets", so booleans suffice —
and in Python that lets you do the whole DP as a single integer bitmask:
`bits |= bits << num`, then test `bits >> target & 1`. That is a ~64× constant
factor from word-level parallelism and it is worth mentioning even if you write
the readable version.
""",
        ),
        (
            "The loop direction that decides it",
            """
Sweep the target **downwards**, from `target` to `num`:

```python
for t in range(target, num - 1, -1):
    reachable[t] |= reachable[t - num]
```

Going upwards is the single bug that gets this problem wrong, and it does not
crash — it silently answers a different question. Ascending, `reachable[t-num]`
may have already been switched on *by this same `num`*, so the element gets
spent more than once. That is **unbounded** knapsack (Coin Change / Combination
Sum), not 0/1.

The test that exposes it: `[1, 5]`. Total 6, target 3, and no subset sums to 3,
so the answer is **false**. An ascending loop reaches 1, then 2, then 3 by
reusing the single `1` three times and reports true. It is in the cases below
for exactly that reason — the LeetCode samples do not catch it.

Also worth an early exit: once `reachable[target]` is true you can stop.

On the empty array this returns **true** — target 0, and the empty subset
already hits it, so the two halves are both empty. LeetCode guarantees
`n ≥ 1`, so state that convention rather than letting the interviewer guess
which way your code falls.
""",
        ),
    ],
}


def can_partition(nums: list[int]) -> bool:
    total = sum(nums)
    if total % 2:
        return False  # an odd total can never split evenly

    target = total // 2
    reachable = [False] * (target + 1)
    reachable[0] = True  # the empty subset

    for num in nums:
        # descending: each num updates only slots that predate it
        for t in range(target, num - 1, -1):
            if reachable[t - num]:
                reachable[t] = True
        if reachable[target]:
            return True

    return reachable[target]


CASES = [
    (([1, 5, 11, 5],), True),
    (([1, 2, 3, 5],), False),
    (([1, 5],), False),
    (([2, 2, 3, 5],), False),
    (([3, 3, 3, 4, 5],), True),
    (([1, 1],), True),
    (([100],), False),
    (([],), True),
]


def solve(nums: list[int]) -> bool:
    return can_partition(nums)
