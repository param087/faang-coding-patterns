"""Maximum Subarray — LeetCode 53."""

from __future__ import annotations

META = {
    "pattern": "divide-and-conquer",
    "symbol": "max_sub_array",
    "insight": "If the running total has gone negative it can only hurt what follows — drop it and start fresh.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
The largest sum of a contiguous non-empty subarray.

Ask: **must the subarray be non-empty?** (Yes — otherwise an all-negative array
answers 0, and that changes the base case.) Contiguous (yes). Return the sum or
the indices?
""",
        ),
        (
            "Why it is asked",
            """
This problem is on the divide-and-conquer page for a reason: it has a
well-known O(n log n) D&C solution (best-left, best-right, best-crossing) that
is a classic teaching example — and it is **worse than the right answer**.

The question is really testing whether you reach for the appropriate tool
rather than the impressive one.
""",
        ),
        (
            "Kadane's insight",
            """
At each element, the best subarray **ending here** is either:

- that element alone, or
- that element appended to the best subarray ending at the previous position.

Which means: if the running total has gone negative, it can only hurt whatever
follows, so drop it and start fresh.

One line of state, O(n) time, O(1) space.
""",
        ),
        (
            "The edge case",
            """
Initialise from `nums[0]`, **not** 0.

Seeding with 0 returns 0 for `[-1]`, because the algorithm silently treats the
empty subarray as an option. That is the test they run, and it is the only bug
this problem has.
""",
        ),
        (
            "Dry run",
            """
`[-2,1,-3,4,-1,2,1,-5,4]` → **6** (the subarray `[4,-1,2,1]`).

Trace the moment at index 3: the running total is −2, so `max(4, -2 + 4)`
picks 4 and abandons everything before it. That single comparison is the whole
algorithm.
""",
        ),
        (
            "Follow-ups",
            """
- **Return the subarray itself** — track a start index that resets whenever
  you start fresh, and record the best pair.
- **Maximum Sum Circular Subarray** — `max(normal_kadane, total -
  minimum_kadane)`, with a special case when every element is negative (the
  "wrap" answer would be the empty subarray).
- **Maximum Product Subarray** — track both the max *and* the min running
  product, because a negative times a negative flips.
""",
        ),
    ],
}


def max_sub_array(nums: list[int]) -> int:
    # Seed from nums[0], not 0 — the subarray must be non-empty.
    best = current = nums[0]

    for value in nums[1:]:
        # Extend, or abandon a negative running total and start here.
        current = max(value, current + value)
        best = max(best, current)

    return best


CASES = [
    (([-2, 1, -3, 4, -1, 2, 1, -5, 4],), 6),
    (([1],), 1),
    (([5, 4, -1, 7, 8],), 23),
    (([-1],), -1),
    (([-2, -1],), -1),
    (([-3, -2, -5],), -2),
]


def solve(nums: list[int]) -> int:
    return max_sub_array(nums)
