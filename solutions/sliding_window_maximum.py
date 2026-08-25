"""Sliding Window Maximum — LeetCode 239."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "monotonic-stack",
    "insight": "A value smaller than a later one is useless forever — every future window containing it also contains the bigger one.",
    "time": "O(n)",
    "space": "O(k)",
    "sections": [
        (
            "What it asks",
            """
Return the maximum of every window of size `k` as it slides across the array.

Ask: is `k` guaranteed at most `n` (yes); can values be negative (yes); is the
expected complexity O(n) (yes — that is what rules out the heap).
""",
        ),
        (
            "Why the heap is the wrong answer",
            """
A max-heap of the window works and is O(n log n). If the bound is n ≤ 10⁵ it
passes; at 10⁶ it may not.

But the real reason to prefer the deque is different: **a heap cannot delete
the element leaving the window.** You would need lazy deletion — push
`(value, index)` and discard stale roots — and explaining that costs more time
than writing the deque.

Say all of this. Knowing why the obvious structure does not fit is the signal.
""",
        ),
        (
            "The insight",
            """
If `nums[j] <= nums[i]` and `j < i`, then `j` is **useless forever**: every
future window that contains `j` also contains `i`, which is at least as large.

So the deque only ever holds a decreasing sequence of genuine *candidates*,
and the front is always the current window's maximum.
""",
        ),
        (
            "Why a deque and not a stack",
            """
A stack cannot evict from the bottom, and a sliding window must: once an index
falls out of range it has to go, even though it may still be the maximum of
what is behind it.

So you pop from **both** ends — the back for values that can never win again,
the front for values that have aged out.
""",
        ),
        (
            "Dry run",
            """
`[1, 3, -1, -3, 5, 3, 6, 7]`, k = 3.

- Push 1. 3 arrives and **evicts 1** — 1 can never win again.
- −1 and −3 stack up behind 3 (they are smaller, so they are still candidates
  for later windows).
- First answer: **3**.
- When 5 arrives it evicts −3, then −1, then 3 — leaving just 5.

That eviction cascade is the amortised argument made visible: each index
enters and leaves the deque exactly once, so the whole scan is O(n).
""",
        ),
        (
            "The off-by-one",
            """
The front-eviction check is `window[0] <= i - k`. Getting it wrong silently
returns the *previous* window's answer, which looks almost right.

And `if i >= k - 1` is what stops you emitting answers before the first full
window exists.
""",
        ),
        (
            "Follow-ups",
            """
- **Sliding window median.** The deque does not help — medians need order
  statistics, so it becomes two heaps or an
  [ordered multiset](../../patterns/ordered-set/). Knowing which follow-ups a
  pattern does *not* cover is worth as much as knowing which it does.
- **Sliding window minimum** — flip the comparison.
- **Constrained Subsequence Sum** — a DP whose transition is a window maximum,
  solved with this exact deque.
""",
        ),
    ],
}


def max_sliding_window(nums: list[int], k: int) -> list[int]:
    if k <= 0 or not nums:
        return []

    window: deque[int] = deque()  # indices, values decreasing front -> back
    result: list[int] = []

    for i, value in enumerate(nums):
        # Anything smaller can never be a maximum again.
        while window and nums[window[-1]] <= value:
            window.pop()
        window.append(i)

        if window[0] <= i - k:  # the front has aged out of the window
            window.popleft()

        if i >= k - 1:  # only emit once a full window exists
            result.append(nums[window[0]])

    return result


CASES = [
    (([1, 3, -1, -3, 5, 3, 6, 7], 3), [3, 3, 5, 5, 6, 7]),
    (([1], 1), [1]),
    (([1, -1], 1), [1, -1]),
    (([9, 8, 7], 2), [9, 8]),
    (([7, 2, 4], 2), [7, 4]),
    (([], 3), []),
]


def solve(nums: list[int], k: int) -> list[int]:
    return max_sliding_window(nums, k)
