"""Minimum Size Subarray Sum — LeetCode 209."""

from __future__ import annotations

META = {
    "pattern": "sliding-window",
    "insight": "With strictly positive values the window sum rises as it grows, so the moment the target is met you shrink and record.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
The shortest contiguous subarray whose sum is **at least** `target`. Zero if
no subarray reaches it.

The clarifying question that decides the whole solution: **are the values
strictly positive?** LeetCode says yes. If zeros or negatives are allowed the
window is dead on arrival — see the follow-ups — so ask before you commit, and
say why you are asking.

Also confirm "at least", not "equal to". Equality with positives is a
different problem and usually wants a prefix-sum map.
""",
        ),
        (
            "The insight",
            """
Positivity makes the window sum **monotone in width**: extending right can
only increase it, moving left in can only decrease it. That gives a decision
rule with no search in it —

- sum below target → the window is too small, so grow right;
- sum at or above target → record the width, then shrink from the left,
  because any longer window ending here is already worse.

Note where the recording happens: **inside the shrink loop**, while the window
is still valid. That is the mirror image of the maximum-window problems, where
you repair first and measure after. Getting this backwards is the single most
common way this loop is written wrong.

Each index enters once and leaves once, so despite the nested `while` it is
one linear pass.
""",
        ),
        (
            "Follow-ups",
            """
- **"Now do it in O(n log n)"** — the stated LeetCode follow-up. Prefix sums
  are strictly increasing (positives again), so for each right end binary
  search the largest left with `prefix[right] - prefix[left] >= target`.
  Slower in practice, but it is the answer they want, and it generalises to
  parallel/immutable settings.
- **Negatives allowed** — the window breaks, because shrinking can now
  *raise* the sum and there is no valid stopping rule. This becomes LeetCode
  862, Shortest Subarray with Sum at Least K, which needs a monotonic deque
  over prefix sums. Naming 862 is a strong signal that you understand *why*
  the two-pointer works here rather than having memorised it.
- **Smallest window with sum exactly `target`** — prefix sums in a hash map,
  storing the latest index per sum.
""",
        ),
    ],
}


def min_subarray_len(target: int, nums: list[int]) -> int:
    left = 0
    running = 0
    best = len(nums) + 1  # sentinel: wider than any real window

    for right, value in enumerate(nums):
        running += value
        while running >= target:  # record while still valid, then shrink
            best = min(best, right - left + 1)
            running -= nums[left]
            left += 1

    return 0 if best == len(nums) + 1 else best


CASES = [
    ((7, [2, 3, 1, 2, 4, 3]), 2),
    ((4, [1, 4, 4]), 1),
    ((11, [1, 1, 1, 1, 1, 1, 1, 1]), 0),
    ((11, [1, 2, 3, 4, 5]), 3),
    ((15, [1, 2, 3, 4, 5]), 5),
    ((16, [1, 2, 3, 4, 5]), 0),
    ((1, [1]), 1),
    ((5, []), 0),
]


def solve(target: int, nums: list[int]) -> int:
    return min_subarray_len(target, nums)
