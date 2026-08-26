"""Maximum Width Ramp — LeetCode 962."""

from __future__ import annotations

META = {
    "pattern": "monotonic-stack",
    "insight": "Only strictly decreasing prefix minima can ever be the left end of the widest ramp; scan back from the right and pop them greedily.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
A ramp is a pair `i < j` with `nums[i] <= nums[j]`; its width is `j - i`.
Return the widest one, or 0 if none exists.

Two things to pin down: the comparison is **non-strict**, so `[1, 1]` is a ramp
of width 1, and the answer is the width, not the pair. All-pairs is O(n²) —
at n = 5·10⁴ that is 2.5·10⁹ comparisons.
""",
        ),
        (
            "The insight",
            """
Which indices can be the **left** end of the widest ramp? Only those where
`nums[i]` is strictly smaller than everything before it. If some earlier index
`i'` had `nums[i'] <= nums[i]`, then any ramp starting at `i` extends to one
starting at `i'`, which is at least as wide. So the candidate left ends are the
strictly decreasing prefix minima, and one forward pass collects them onto a
stack.

Now walk `j` from the **right** end inwards. While the top candidate satisfies
`nums[top] <= nums[j]`, record `j - top` and pop it: that candidate has just
been paired with the rightmost `j` it will ever see, so it is finished. Once the
stack empties, no wider ramp is possible and you can stop.

Two linear passes, one pop per candidate: O(n).
""",
        ),
        (
            "Why popping is safe",
            """
The uncomfortable step is discarding a candidate the first time it matches.
It is safe because `j` moves **right to left**: the first `j` that pairs with a
candidate is the largest index it can pair with, so its best width is measured
at exactly that moment, and every later `j` is strictly closer.

The other half is that the stack is *decreasing*, so if `nums[top] <= nums[j]`
holds, it may also hold for the next candidate down — hence a `while`, not an
`if`. On `[3, 2, 1, 3]` the final element clears all three candidates in one
go; popping only one per `j` returns 1 instead of 3.

Edge cases that catch a rushed version:

- **`<=` throughout.** `[1, 1, 1, 1]` must return 3; a strict `<` returns 0.
- **Strictly decreasing input** — `[2, 1]` has no ramp, answer 0, and the stack
  never gets popped.
- **Empty or single-element input** — 0, no ramp exists.
- The forward pass appends only when `nums[candidates[-1]] > value`, strictly.
  Appending on equality wastes work and, worse, hides the fact that the later
  duplicate is a strictly worse left end.
""",
        ),
    ],
}


def max_width_ramp(nums: list[int]) -> int:
    candidates: list[int] = []  # indices of strictly decreasing prefix minima
    for i, value in enumerate(nums):
        if not candidates or nums[candidates[-1]] > value:
            candidates.append(i)

    best = 0
    for j in range(len(nums) - 1, -1, -1):
        # `j` is the furthest right partner these candidates will ever see.
        while candidates and nums[candidates[-1]] <= nums[j]:
            best = max(best, j - candidates.pop())
        if not candidates:  # nothing left can start a wider ramp
            break

    return best


CASES = [
    (([6, 0, 8, 2, 1, 5],), 4),
    (([9, 8, 1, 0, 1, 9, 4, 0, 4, 1],), 7),
    # One `j` clears the whole candidate stack — the `while`-not-`if` case.
    (([3, 2, 1, 3],), 3),
    # Equal values still form a ramp.
    (([1, 1, 1, 1],), 3),
    # Strictly decreasing: no ramp at all.
    (([2, 1],), 0),
    (([5, 4, 3, 2, 1],), 0),
    (([1, 2],), 1),
    (([-5, -3, 0, -1],), 3),
    (([5],), 0),
    (([],), 0),
]


def solve(nums: list[int]) -> int:
    return max_width_ramp(nums)
