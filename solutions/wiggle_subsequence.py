"""Wiggle Subsequence — LeetCode 376."""

from __future__ import annotations

META = {
    "pattern": "greedy",
    "insight": "Only direction changes matter, so count them: the answer is the number of alternations in the sign of consecutive differences, plus one.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Longest subsequence (delete elements, keep order) whose consecutive
differences **strictly alternate** in sign. A single element is a wiggle of
length 1; two equal elements are not a wiggle, because a difference of zero has
no sign.

Ask about equals early — `[3, 3, 3]` answers 1, not 3, and a solution that
treats `>=` as "up" is wrong before it starts.
""",
        ),
        (
            "The insight",
            """
Inside a monotone run, only the **endpoint** is ever worth keeping: if the
sequence rises through `2, 5, 9`, taking the 5 as well would need two
consecutive positive differences, which is banned. So the answer is one plus
the number of times the sign of `nums[i] - nums[i-1]` flips, ignoring zeros.

Carry two counters — the length of the best wiggle ending on an **up** step and
the best ending on a **down** step — and update only the one matching the
current step:

```
nums[i] > nums[i-1]  ->  up   = down + 1
nums[i] < nums[i-1]  ->  down = up + 1
equal                ->  neither moves
```

`up = down + 1` is doing the flattening for you: extending the best
down-ending sequence by one rising step. Because a longer run just reassigns
`up` from the same `down`, interior elements of a run cost nothing.

There is an O(n²) LIS-style DP for this, and interviewers will accept it as a
first pass. Getting to O(n) with two integers is the point.
""",
        ),
        (
            "Edge cases",
            """
- **Empty input → 0**, single element → 1. The two-counter version starts both
  at 1, so the empty case must be guarded before the loop or you return 1.
- **Plateaus.** `[1, 2, 2, 1]` is 3 (`1, 2, 1`): the repeat is skipped, not
  treated as a flip. Any strict-vs-non-strict slip shows up here first.
- **Fully monotone input** answers 2, not n — `[1, 2, 3, 4, 5]` keeps only the
  two endpoints.
- **Leading plateau**, `[0, 0, 0, 5]` → 2. Zeros before the first real step
  must not seed a direction.
- Follow-up worth naming: if the subsequence had to be **contiguous**, the
  greedy collapses to a straightforward reset-on-failure scan — a different
  problem with a much simpler answer.
""",
        ),
    ],
}


def wiggle_max_length(nums: list[int]) -> int:
    if not nums:
        return 0

    up = down = 1  # best wiggle ending on a rise / on a fall

    for previous, current in zip(nums, nums[1:], strict=False):
        if current > previous:
            up = down + 1
        elif current < previous:
            down = up + 1
        # equal: no sign, so neither counter moves

    return max(up, down)


CASES = [
    (([1, 7, 4, 9, 2, 5],), 6),
    (([1, 17, 5, 10, 13, 15, 10, 5, 16, 8],), 7),  # runs collapse to endpoints
    (([1, 2, 3, 4, 5, 6, 7, 8, 9],), 2),
    (([1, 2, 2, 1],), 3),  # the plateau is skipped, not counted
    (([3, 3, 3, 3],), 1),
    (([0, 0, 0, 5],), 2),  # leading plateau seeds no direction
    (([1],), 1),
    (([],), 0),
]


def solve(nums: list[int]) -> int:
    return wiggle_max_length(nums)
