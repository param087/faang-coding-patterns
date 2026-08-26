"""Longest Continuous Subarray With Absolute Diff Less Than or Equal to Limit — LeetCode 1438."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "ordered-set",
    "insight": "A window is valid exactly when max - min <= limit, so keep both extremes live in two monotonic deques and shrink only when the gap breaks.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
The longest **contiguous** subarray whose largest and smallest elements differ
by at most `limit`. ("Continuous" in the title means contiguous — worth
confirming, because a subsequence version would be a sorting problem.)

Ask: can `limit` be 0? Yes — then the answer is the longest run of equal
values, which is the case that breaks any solution comparing with `<` where it
should use `<=`. Values reach 10⁹ and n reaches 10⁵, so an O(n²) scan over
windows is 10¹⁰ operations.
""",
        ),
        (
            "The insight",
            """
Validity is **monotone**: if `[l, r]` has `max - min <= limit`, so does every
subarray inside it. That is exactly the precondition for a sliding window —
extend right, and when the window breaks, advance left until it heals.

The only quantity that decides validity is `max - min` over the current window,
so the real question is *which structure gives both extremes of a window that
grows on the right and shrinks on the left*:

- **An ordered multiset** (`SortedList`, or `TreeMap<value, count>` in Java) —
  `first()` and `last()` are the extremes and the leaving element is removed
  exactly. O(n log n), and the answer to say first because it is the one that
  generalises. Not standard library in Python.
- **Two heaps with lazy deletion** — works, but the stale entries have to be
  validated against `left` on every peek.
- **Two monotonic deques** — a decreasing one holding candidate maxima, an
  increasing one holding candidate minima. Every index is pushed once and
  popped once, so the whole scan is **O(n)** and there is nothing to delete
  lazily.

The deques are the version to write. Name the multiset first anyway: it shows
you know why the deques work.
""",
        ),
        (
            "The shrink step, which is where it breaks",
            """
Three details, and each has a failure that survives the samples:

- **The deques hold indices, not values.** When `left` advances you must know
  whether the element leaving the window is the one currently sitting at the
  front. `if maxima[0] == left: maxima.popleft()` needs an index to compare.
  Store values and you cannot tell a stale front from a duplicate.
- **Pop the front only when its index equals `left`.** Popping both fronts
  unconditionally every time you shrink throws away elements that are still
  inside the window, and the answer comes out too small.
- **Shrink with `while`, not `if`.** One removal need not restore validity: on
  `[1, 2, 3, 10]` with `limit = 2`, the arrival of `10` drags `left` from 0 to
  3 — three removals inside a single iteration. Re-test
  `nums[maxima[0]] - nums[minima[0]] > limit` after every step.

Two smaller ones: pop the back with strict `<` / `>` so equal values stay in
the deque — that keeps `limit = 0` working — and measure the window as
`right - left + 1` *after* shrinking, never before.
""",
        ),
    ],
}


def longest_subarray(nums: list[int], limit: int) -> int:
    maxima: deque[int] = deque()  # indices, values non-increasing front -> back
    minima: deque[int] = deque()  # indices, values non-decreasing front -> back
    left = 0
    best = 0

    for right, value in enumerate(nums):
        while maxima and nums[maxima[-1]] < value:  # strict: keep duplicates
            maxima.pop()
        maxima.append(right)

        while minima and nums[minima[-1]] > value:
            minima.pop()
        minima.append(right)

        while nums[maxima[0]] - nums[minima[0]] > limit:
            if maxima[0] == left:  # only the element actually leaving
                maxima.popleft()
            if minima[0] == left:
                minima.popleft()
            left += 1

        best = max(best, right - left + 1)

    return best


CASES = [
    (([8, 2, 4, 7], 4), 2),
    (([10, 1, 2, 4, 7, 2], 5), 4),
    (([4, 2, 2, 2, 4, 4, 2, 2], 0), 3),  # limit 0: the longest equal run
    (([1, 5, 6, 7, 8, 10, 6, 5, 6], 4), 5),  # the window must survive a spike
    (([-5, -3, 10, -3, -5], 2), 2),  # negatives
    (([1, 2, 3, 4, 5], 100), 5),  # never shrinks
    (([5], 0), 1),
    (([], 7), 0),
]


def solve(nums: list[int], limit: int) -> int:
    return longest_subarray(nums, limit)
