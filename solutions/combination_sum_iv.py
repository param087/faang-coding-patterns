"""Combination Sum IV — LeetCode 377."""

from __future__ import annotations

META = {
    "pattern": "dp-1d",
    "insight": "Despite the name it counts ordered sequences, and that is decided purely by which loop is on the outside.",
    "time": "O(target · n)",
    "space": "O(target)",
    "sections": [
        (
            "What it asks",
            """
Given distinct positive integers and a target, count the ways to add up to the
target with unlimited reuse — where **different orderings count separately**.
For `[1, 2, 3]` and target 4 the answer is 7, because `(1,3)` and `(3,1)` are
both counted.

The title says "combination" and the problem means *permutation*. Say that out
loud and confirm it with the interviewer; getting this backwards produces a
clean, working solution to the wrong question and it is the entire point of
the problem.
""",
        ),
        (
            "The insight",
            """
Classify by the **first element of the sequence**. Any ordered sequence summing
to `t` starts with some `num`, and the rest is an ordered sequence summing to
`t - num`:

```
dp[t] = Σ dp[t - num] for every num ≤ t,  dp[0] = 1
```

`dp[0] = 1` is the empty sequence — the base case that makes the sum come out
right, not a special case.

Now the part that decides the problem: **target on the outside, numbers on the
inside**.

```python
for t in range(1, target + 1):
    for num in nums:
        ...
```

Every `(t, position)` pair gets to try every number, so each ordering is
generated once. Swap the loops — numbers outside, target inside — and you fix
a canonical order in which coins may be used, which counts *unordered*
combinations. That swapped version is Coin Change II (LC 518), the correct
answer to a different question. On `[1, 2, 3]`, target 4: 7 with this loop
order, 4 with the other.

That is worth memorising as a pair, because "which loop is outside" is the
single most common interview question about counting DP.
""",
        ),
        (
            "The follow-up they always ask",
            """
**"What if negative numbers were allowed?"** The problem statement itself
raises this, so have the answer ready: the count becomes **infinite**. With
`[-1, 1]` and target 1 you can pad any solution with `+1, -1` forever, and the
DP breaks because `dp[t]` would depend on `dp[t + 1]` — the recurrence is no
longer acyclic. The fix is to bound the sequence length, which adds a second
dimension: `dp[length][t]`, O(target · maxLen · n).

Two smaller points:

- **Sort `nums` and `break`** once `num > t`. Same complexity, roughly halves
  the work, and costs one line.
- **Recursive + `@cache` on the target** is the same algorithm and is often
  faster to write under pressure. It also makes the permutation semantics
  obvious: you sum over *all* numbers at every level, with no index carried
  down. Carrying a start index down is precisely what would turn it into the
  combination count.
- `target = 0` returns **1**, the empty sequence. LeetCode's constraints start
  at 1, but the base case has to be 1 regardless or the whole table collapses
  to zero.
""",
        ),
    ],
}


def combination_sum4(nums: list[int], target: int) -> int:
    ordered = sorted(nums)
    ways = [0] * (target + 1)
    ways[0] = 1  # the empty sequence

    # target outside, numbers inside -> every ordering counted separately
    for t in range(1, target + 1):
        for num in ordered:
            if num > t:
                break
            ways[t] += ways[t - num]

    return ways[target]


CASES = [
    (([1, 2, 3], 4), 7),
    (([1, 2], 3), 3),
    (([2, 3], 7), 3),
    (([9], 3), 0),
    (([1], 5), 1),
    (([2, 4], 5), 0),
    (([1, 2, 3], 0), 1),
    (([3, 33, 333], 10000), 0),
]


def solve(nums: list[int], target: int) -> int:
    return combination_sum4(nums, target)
