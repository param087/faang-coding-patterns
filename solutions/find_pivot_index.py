"""Find Pivot Index — LeetCode 724."""

from __future__ import annotations

META = {
    "pattern": "prefix-sums",
    "insight": "You never need the right-hand sum: it is total - left - nums[i], so one running total and the grand total suffice.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Find the leftmost index where the sum of everything strictly to its left equals
the sum of everything strictly to its right. The pivot itself belongs to
neither side. Return `-1` if there is none.

Ask: **can values be negative?** (Yes — and that kills every two-pointer or
early-exit idea, so it is the question worth asking.) And confirm *leftmost*,
because ties are common in arrays full of zeros.
""",
        ),
        (
            "The insight",
            """
The naive fix for the O(n²) rescan is two prefix arrays, one from each end.
You do not need either.

Sum the array once. Then walk left to right carrying `left`, the sum of
everything before `i`:

```
right = total - left - nums[i]
```

The right-hand side is fully determined by two numbers you already have, so the
whole thing is O(1) space. Compare, then do `left += nums[i]` **after** the
comparison — updating before it silently includes the pivot in its own left
side.
""",
        ),
        (
            "The edge cases that decide it",
            """
- **Index 0 can be the pivot.** Its left sum is the empty sum, `0`. Anyone who
  starts the loop at `i = 1` fails on `[-1, -1, -1, 0, 1, 1]`, whose answer is
  `0`. Likewise the last index, whose right sum is `0`.
- **Negatives mean no early exit.** With all-positive values you could stop
  once `left > total / 2`; here `[2, 1, -1]` pivots at index 0 with a
  right-hand sum of `0`. Do not import that optimisation from a similar-looking
  problem.
- **Leftmost, not any.** `[0, 0, 0]` has three valid pivots; the answer is `0`.
  Return on the first hit rather than collecting them.
- **Empty array** returns `-1`, and a single element returns `0` — both sides
  are empty, so `[7]` pivots at `0` even though `7 != 0`.
- **Overflow** does not exist in Python, but in Java `total` needs `long` once
  n = 10⁴ and values reach 1000 — mention it, then move on.
""",
        ),
    ],
}


def pivot_index(nums: list[int]) -> int:
    total = sum(nums)
    left = 0

    for i, value in enumerate(nums):
        # Everything after i, without ever building a suffix array.
        if left == total - left - value:
            return i
        left += value  # after the comparison: the pivot is in neither side

    return -1


CASES = [
    (([1, 7, 3, 6, 5, 6],), 3),
    (([1, 2, 3],), -1),
    (([-1, -1, -1, 0, 1, 1],), 0),
    (([-1, -1, -1, -1, -1, 0],), 2),
    (([2, 1, -1],), 0),
    (([0, 0, 0],), 0),
    (([7],), 0),
    (([],), -1),
]


def solve(nums: list[int]) -> int:
    return pivot_index(nums)
