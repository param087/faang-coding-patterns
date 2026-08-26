"""Trapping Rain Water — LeetCode 42."""

from __future__ import annotations

META = {
    "pattern": "two-pointers",
    "insight": "Water over a bar is min(tallest left, tallest right) minus its height — and the shorter side already knows its own answer.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Bars of unit width and given heights; return how much rain settles between
them. Worth confirming: bars have no thickness cost, water only pools where a
taller bar exists on **both** sides, and the answer is a single total, not a
per-column breakdown.
""",
        ),
        (
            "The insight",
            """
Fix your attention on one column `i`. The water standing above it is

```
min(max height to its left, max height to its right) - height[i]
```

clamped at zero. Nothing else about the array matters. That single formula
turns a "simulate the rain" problem into a lookup problem.

The direct implementation scans left and right for every `i`: **O(n²)**, which
at n = 2·10⁴ is 4·10⁸ operations — too slow, and it is the answer most people
give first. Precomputing two prefix-max arrays fixes the time but costs O(n)
space.

The two-pointer version gets both. Walk `lo` and `hi` inwards, carrying
`left_max` and `right_max`. **Process whichever side is shorter.** If
`height[lo] < height[hi]`, then `right_max >= height[hi] > height[lo]`, so the
right wall is guaranteed to be at least as tall as anything on the left — which
means `min(left_max, right_max) == left_max` for column `lo`, and `left_max` is
already known exactly. Settle that column and advance.
""",
        ),
        (
            "The detail that decides it",
            """
The comparison is between **`height[lo]` and `height[hi]`**, not between
`left_max` and `right_max`. Both variants happen to work, but only the first
one has the clean justification above, and mixing them — comparing the maxima
while updating from the raw heights — produces a version that is wrong on
asymmetric input and right on the sample.

Dry run `[4, 2, 0, 3, 2, 5]` → **9**:

- `lo=0 (4)`, `hi=5 (5)`. Left is shorter, `left_max = 4`, no water at a peak.
- `lo=1 (2)`: still shorter than 5. `4 - 2 = 2`.
- `lo=2 (0)`: `4 - 0 = 4`. Running total 6.
- `lo=3 (3)`: `4 - 3 = 1`. Total 7.
- `lo=4 (2)`: `4 - 2 = 2`. Total **9**.

Note the pointers never met a taller right bar than 5 — the right side was
never processed at all, and that is fine. Compare against `[4, 2, 3]` → **1**,
where the *right* side is the shorter one and the mirrored branch runs.

Both `[]` and a single bar return 0; the loop guard `lo < hi` handles them
without a special case.
""",
        ),
    ],
}


def trap(height: list[int]) -> int:
    lo, hi = 0, len(height) - 1
    left_max = right_max = 0
    water = 0

    while lo < hi:
        if height[lo] < height[hi]:
            # right_max >= height[hi] > height[lo], so left_max is the binding wall
            left_max = max(left_max, height[lo])
            water += left_max - height[lo]
            lo += 1
        else:
            right_max = max(right_max, height[hi])
            water += right_max - height[hi]
            hi -= 1

    return water


CASES = [
    (([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1],), 6),
    (([4, 2, 0, 3, 2, 5],), 9),
    (([4, 2, 3],), 1),  # the mirrored branch: the right wall is the shorter one
    (([2, 0, 2],), 2),
    (([5, 4, 3, 2, 1],), 0),  # monotone: nothing pools
    (([3, 3, 3],), 0),
    (([5],), 0),
    (([],), 0),
]


def solve(height: list[int]) -> int:
    return trap(height)
