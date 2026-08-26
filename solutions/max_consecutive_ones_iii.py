"""Max Consecutive Ones III — LeetCode 1004."""

from __future__ import annotations

META = {
    "pattern": "sliding-window",
    "insight": "Flipping at most k zeros is the same as finding the longest window containing at most k zeros — the flips never need to be chosen.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
A binary array and a budget `k`. Flip at most `k` zeros to ones and return the
longest run of consecutive ones you can end up with.

Ask: **must all k flips be used?** (No.) **Can flips be spent outside the run
you return?** (Pointless — you would never do it, and saying so is what turns
the problem into a window.)
""",
        ),
        (
            "The insight",
            """
Do not think about *which* zeros to flip. Any window containing at most `k`
zeros can be turned into a solid run of ones, and any solid run you could
produce corresponds to such a window. So:

> longest subarray with at most `k` zeros.

That invariant — "at most k zeros" — is monotone in the window: shrinking from
the left can only reduce the zero count, never increase it. Monotonicity is
exactly the property that makes a two-pointer window legal, and it is the
sentence to say before writing the loop.

Track `zeros` only, not the ones. Grow `right` unconditionally, and while the
window holds too many zeros, advance `left`, decrementing `zeros` when the
element leaving is a zero. Record the width after the repair.

`left` never moves backwards, so the inner `while` runs at most n times across
the whole scan: linear, not quadratic.
""",
        ),
        (
            "Edge cases",
            """
- **`k = 0`** — degenerates to "longest run of ones"; `[0, 0, 0]` → `0`, and
  the window correctly collapses to width zero rather than going negative.
- **`k >= number of zeros`** — the answer is the whole array, so the `while`
  never fires. Worth testing, because an off-by-one in the repair loop shows
  up here as `n - 1`.
- **Empty array** → `0`, with no index access.
- The `if` versus `while` choice matters here in a way it does not for
  LeetCode 424: because you record `best` explicitly, a single-step `if`
  leaves an invalid window in place and over-counts. Use `while`.
""",
        ),
    ],
}


def longest_ones(nums: list[int], k: int) -> int:
    left = 0
    zeros = 0
    best = 0

    for right, value in enumerate(nums):
        if value == 0:
            zeros += 1

        while zeros > k:  # repair before measuring
            if nums[left] == 0:
                zeros -= 1
            left += 1

        best = max(best, right - left + 1)

    return best


CASES = [
    (([1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], 2), 6),
    (([0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1], 3), 10),
    (([1, 0, 1, 0, 1], 1), 3),
    (([0, 0, 0], 0), 0),
    (([0, 0, 0], 3), 3),
    (([1, 1, 1], 0), 3),
    (([0], 1), 1),
    (([], 2), 0),
]


def solve(nums: list[int], k: int) -> int:
    return longest_ones(nums, k)
