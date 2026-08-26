"""Jump Game VI — LeetCode 1696."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "monotonic-stack",
    "insight": "The DP is one line; the whole problem is getting max(best[i-k..i-1]) in O(1) with a decreasing deque instead of rescanning the window.",
    "time": "O(n)",
    "space": "O(k) for the deque, O(n) if the DP table is kept",
    "sections": [
        (
            "What it asks",
            """
Start at index 0, and from index `i` you may jump to any index in
`[i + 1, i + k]`. You must finish at the last index. Score is the sum of the
values you land on, including both ends. Maximise it.

The values can be **negative**, which is what makes it a real problem: you are
sometimes forced to eat a loss, and the greedy "always jump to the largest value
in reach" is wrong. On `[-1, 6, 9, -9, -9, -9, -9]` with `k = 2` greedy leaps
straight to the 9, skipping the 6 it could have collected on the way, and then
lands on all four `-9`s for a total of **-28**; the optimum is **-4**
(take the 6 *and* the 9, then step over every other `-9`).

Confirm early that reaching the end is always possible — it is, since `k >= 1`.
""",
        ),
        (
            "The insight",
            """
The recurrence is immediate:

```
best[i] = nums[i] + max(best[i - k] ... best[i - 1])
```

with `best[0] = nums[0]`, and the answer is `best[n - 1]`. Written naively that
is O(n·k), and with n = 10⁵ and k = 10⁵ it is 10¹⁰ operations — the constraints
deliberately allow `k` to be as large as `n`.

So the problem is not the DP, it is the **sliding-window maximum** inside it.
Keep a deque of indices whose `best` values decrease from front to back:

- drop from the **front** any index that has slid out of the window
  (`window[0] < i - k`);
- `best[window[0]]` is then the maximum over the window, in O(1);
- before pushing `i`, drop from the **back** every index whose `best` is `<=`
  `best[i]`, because a newer index with an equal-or-better score dominates an
  older one for every future window.

Each index enters and leaves once: O(n) overall.
""",
        ),
        (
            "The deque against the heap, and the order of operations",
            """
A max-heap of `(best, index)` with lazy deletion also works and is easier to
get right under pressure: pop the top while its index is out of window. That is
O(n log n) and perfectly acceptable — say it, then write the deque, which is
O(n) and the answer being fished for.

Where implementations go wrong:

- **Evict from the front before reading it.** Reading first can return a score
  from an index you are no longer allowed to jump from.
- **Push `i` after computing `best[i]`,** never before — an index cannot be its
  own predecessor.
- **Pop the back on `<=`, not `<`.** With ties the older index is strictly
  worse (it expires sooner), so keeping it costs memory and buys nothing. Both
  are correct; `<=` is tidier.
- The deque stores **indices**, not scores, because the window test is about
  positions.

Negatives never justify a "skip this element" branch: you always land somewhere
in every window of `k`, so the DP already accounts for the forced losses. And
`best` is monotone in nothing at all — do not be tempted by a prefix maximum.
""",
        ),
    ],
}


def max_result(nums: list[int], k: int) -> int:
    if not nums:
        return 0

    best = [0] * len(nums)
    best[0] = nums[0]
    window: deque[int] = deque([0])  # indices, best values decreasing front -> back

    for i in range(1, len(nums)):
        while window and window[0] < i - k:  # evict before reading the front
            window.popleft()
        best[i] = nums[i] + best[window[0]]
        while window and best[window[-1]] <= best[i]:  # a newer, no-worse index dominates
            window.pop()
        window.append(i)

    return best[-1]


CASES = [
    (([1, -1, -2, 4, -7, 3], 2), 7),
    (([10, -5, -2, 4, 0, 3], 3), 17),
    # Every route is a loss; the DP picks the cheapest one.
    (([1, -5, -20, 4, -1, 3, -6, -3], 2), 0),
    # Greedy "jump to the biggest value in reach" scores -28 here.
    (([-1, 6, 9, -9, -9, -9, -9], 2), -4),
    # k = 1 forces every step: no choice at all.
    (([-1, -2, -3], 1), -6),
    # k spanning the whole array: jump straight from first to last.
    (([-1, -2, -3], 5), -4),
    (([100, -1, -100, -1, 100], 4), 200),
    (([7], 3), 7),
    (([], 3), 0),
]


def solve(nums: list[int], k: int) -> int:
    return max_result(nums, k)
