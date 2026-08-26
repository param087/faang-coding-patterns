"""Constrained Subsequence Sum — LeetCode 1425."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "monotonic-stack",
    "insight": "It is a one-line DP whose transition is a maximum over the last k states — which is Sliding Window Maximum, so use the deque.",
    "time": "O(n)",
    "space": "O(n) — O(k) if the deque carries the DP values instead of indices",
    "sections": [
        (
            "What it asks",
            """
Pick a non-empty subsequence of `nums` with the largest sum, subject to: any
two **consecutive chosen** indices are at most `k` apart. Return the sum.

Ask three things before writing anything:

- **Must the subsequence be non-empty?** Yes — and that single word is the
  whole edge case. With an all-negative array the answer is the largest single
  element, not 0.
- Does `k` bound the gap between *chosen* elements, or between all elements?
  Between chosen ones — you may skip up to `k - 1` positions at a time.
- Can values be negative? Yes, which is why this is not just "sum the
  positives".
""",
        ),
        (
            "The insight",
            """
Define `dp[i]` = best sum of a valid subsequence that **ends at `i`**. Then

```
dp[i] = nums[i] + max(0, dp[i-k] … dp[i-1])
```

The `max(0, …)` is the licence to start fresh at `i`: if every reachable
predecessor is a net loss, take `nums[i]` alone. The answer is `max(dp)`, not
`dp[n-1]` — the best subsequence need not run to the end.

Written literally, that inner `max` is an O(k) scan, so O(n·k) overall. At
n = k = 10⁵ that is **10¹⁰ operations**; the constraints are picked precisely
to kill it.

But the transition asks for the maximum of the last `k` DP values, and that is
[Sliding Window Maximum](../sliding-window-maximum/) verbatim. Keep a deque of
indices whose `dp` values decrease front to back: the front is the best
reachable predecessor, and any index with a smaller `dp` than a later one is
useless forever. Each index is pushed once and popped once, so the whole thing
is **O(n)**.

Recognising a known sub-problem inside a DP transition is the actual skill
here — the rest is bookkeeping.
""",
        ),
        (
            "The two bugs that decide it",
            """
**1. Seeding the answer at 0.** `best = 0` silently allows the empty
subsequence, so `[-2, -3, -1]` returns 0 instead of **-1**. Start `best` at
negative infinity (or at `dp[0]`) and let the DP speak.

**2. The expiry off-by-one.** In Sliding Window Maximum the window is
`[i-k+1, i]`, so the front check is `window[0] <= i - k`. Here the window is
`[i-k, i-1]` — `i` itself is not a candidate for its own transition — so the
check is strictly `window[0] < i - k`. Copying the `<=` from the sibling
problem drops the oldest legal predecessor and quietly returns a smaller sum:
on `[5, -10, 1, 1]` with `k = 2` it gives 5 instead of **7**.

Also note the front is **read, not popped**, when it is used: index 0 can be
the best predecessor for indices 1 through `k`. Only expiry and domination
remove things.

Space is `O(n)` because of the `dp` array, but only the last `k` entries are
ever read — store the DP value alongside the index in the deque and it drops
to `O(k)`.
""",
        ),
    ],
}


def constrained_subset_sum(nums: list[int], k: int) -> int:
    if not nums:  # the problem guarantees n >= 1; be explicit anyway
        return 0

    dp = [0] * len(nums)
    window: deque[int] = deque()  # indices, dp values decreasing front -> back
    best = float("-inf")

    for i, value in enumerate(nums):
        while window and window[0] < i - k:  # strictly older than i - k is unreachable
            window.popleft()

        # Extend the best reachable predecessor, or start a fresh subsequence at i.
        dp[i] = value + max(0, dp[window[0]] if window else 0)

        while window and dp[window[-1]] <= dp[i]:  # dominated forever
            window.pop()
        window.append(i)

        best = max(best, dp[i])

    return int(best)


CASES = [
    (([10, 2, -10, 5, 20], 2), 37),
    (([-5, -1, -3], 2), -1),  # non-empty: the answer is the best single element
    (([10, -2, -10, -5, 20], 2), 23),  # worth crossing a negative to reach the 20
    (([1, -3, 4, -1, 2], 1), 5),  # k = 1 degenerates to Kadane
    (([5, -10, 1, 1], 2), 7),  # breaks the `<= i - k` expiry off-by-one
    (([1, -1, 2, -1, 3], 5), 6),  # k >= n: just take every positive
    (([-1], 1), -1),
    (([], 3), 0),
]


def solve(nums: list[int], k: int) -> int:
    return constrained_subset_sum(nums, k)
