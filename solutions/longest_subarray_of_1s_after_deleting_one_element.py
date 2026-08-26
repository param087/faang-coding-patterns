"""Longest Subarray of 1's After Deleting One Element — LeetCode 1493."""

from __future__ import annotations

META = {
    "pattern": "sliding-window",
    "insight": "The deletion is compulsory, so the answer is the widest window holding at most one zero, minus one.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Delete **exactly one** element from a binary array and return the length of
the longest run of ones that remains. Return `0` if no run survives.

The word doing all the work is *exactly*. You must delete something even when
the array is all ones — which is why `[1, 1, 1]` answers `2`, not `3`. Confirm
this with the interviewer; it is the whole difference between this and Max
Consecutive Ones III with `k = 1`.
""",
        ),
        (
            "The insight",
            """
The element you delete is either the one zero inside your chosen window or, if
the window has no zero, a one you sacrifice. Either way you lose exactly one
element from the window.

So: widest window containing **at most one zero**, then subtract 1.

That "subtract 1" handles both branches at once, which is the neat part —
you never branch on whether a zero was present. Grow `right`, and while the
window holds two zeros, walk `left` forward until it holds one again. Record
`right - left` (already the width minus one).

`left` is monotone, so the nested `while` still gives a single linear pass.
""",
        ),
        (
            "Edge cases",
            """
- **All ones** — `[1, 1, 1]` → `2`. A solution that maxes over
  `right - left + 1` and only subtracts when a zero was seen returns 3 here.
  This is the case interviewers actually run.
- **All zeros** — `[0, 0, 0]` → `0`. `right - left` never exceeds 0, so no
  special case is needed, but check it: a version that returns `best - 1` at
  the end would produce `-1`.
- **Single element** — `[1]` → `0`, since the only element must go.
- **Empty array** — `0`, with no index access. Out of LeetCode's constraints,
  in scope for a real review.
- **Two zeros adjacent**, `[1, 0, 0, 1]` → `1`: the window can never span
  both, which is exactly what the repair loop enforces.
""",
        ),
    ],
}


def longest_subarray(nums: list[int]) -> int:
    left = 0
    zeros = 0
    best = 0

    for right, value in enumerate(nums):
        if value == 0:
            zeros += 1

        while zeros > 1:
            if nums[left] == 0:
                zeros -= 1
            left += 1

        best = max(best, right - left)  # width minus the compulsory deletion

    return best


CASES = [
    (([1, 1, 0, 1],), 3),
    (([0, 1, 1, 1, 0, 1, 1, 0, 1],), 5),
    (([1, 1, 1],), 2),
    (([1, 1, 1, 0, 1, 1, 1],), 6),
    (([1, 0, 0, 1],), 1),
    (([0, 0, 0],), 0),
    (([1],), 0),
    (([],), 0),
]


def solve(nums: list[int]) -> int:
    return longest_subarray(nums)
