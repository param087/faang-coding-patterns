"""Contains Duplicate III — LeetCode 220."""

from __future__ import annotations

from bisect import bisect_left, insort

META = {
    "pattern": "ordered-set",
    "insight": "Ask the window only for the value nearest nums[i]; bucketing by width t+1 turns that neighbour query into a dict lookup.",
    "time": "O(n)",
    "space": "O(min(n, indexDiff))",
    "sections": [
        (
            "What it asks",
            """
Is there a pair `i != j` with `|i - j| <= indexDiff` **and**
`|nums[i] - nums[j]| <= valueDiff`? Two constraints at once — one on position,
one on value — which is what makes it harder than Contains Duplicate II.

Worth asking:

- **Can `valueDiff` be 0?** Yes. Then the question collapses to "a repeat
  inside the window", and any solution that divides by `valueDiff` dies.
- **Are values 32-bit?** They are, and `|nums[i] - nums[j]|` can reach 2³²,
  which overflows `int` in Java/C++. Python does not care, but say it — it is
  the difference between a passing and a failing submission in another
  language, and interviewers who set this problem know that.
- `|i - j| <= indexDiff` means a window of `indexDiff + 1` entries counting
  the current one.
""",
        ),
        (
            "Brute force, and why it fails",
            """
For each `i`, compare against the previous `indexDiff` entries: O(n · k).
With n = 10⁵ and `indexDiff` = 10⁵ that is **10¹⁰ comparisons**, and the
constraints deliberately allow `indexDiff` to be as large as n.
""",
        ),
        (
            "The ordered-set answer",
            """
Keep the last `indexDiff` values as a **sorted multiset**. For a new value `v`
you do not need to look at every element — only at the one closest to `v`:

```
candidate = ceiling(v - valueDiff)      # smallest element >= v - valueDiff
hit       = candidate is not None and candidate <= v + valueDiff
```

One ceiling query decides the whole window, because if anything at all lies in
`[v - t, v + t]`, the smallest element `>= v - t` does.

That is O(n log k) — in Java. **Python has no ordered set in the standard
library**, and this is where the interview decision actually lives:

- `sortedcontainers.SortedList` — true O(log k) insert and search, but a third
  party package. LeetCode ships it; a CoderPad session may not.
- `bisect` + `insort` on a list — O(log k) search but **O(k) insert**, so the
  worst case is back to 10¹⁰ element moves (fast ones, but still).

Both are written below. Say which you are reaching for and why, then show the
version that does not need either.
""",
        ),
        (
            "Bucketing: the same query in O(1)",
            """
Give each value a bucket of width `valueDiff + 1`:

```
key = value // (valueDiff + 1)
```

Two values in the **same bucket** differ by at most `valueDiff` — that is a hit
with no comparison at all. Two values within `valueDiff` of each other that are
*not* in the same bucket must be in **adjacent** buckets, so exactly three keys
need checking: `key - 1`, `key`, `key + 1`.

Each bucket only ever needs to hold **one** value, because the moment a second
one arrives you have already returned `True`.

That drops the whole thing to O(n) time and O(min(n, indexDiff)) space, and it
sidesteps the missing-ordered-set problem entirely.
""",
        ),
        (
            "The three details that decide it",
            """
- **Width is `valueDiff + 1`, not `valueDiff`.** With width `t`, two values `t`
  apart can land in different buckets *and* the adjacent-bucket test uses `<`,
  and you drop pairs. With `t = 0` a width of `0` is a division by zero.
- **Floor division, not truncation.** Python's `//` floors, so `-1 // 7 == -1`.
  C++/Java integer division truncates toward zero, so `-1 / 7 == 0` — the same
  bucket as `3`, and `[-1, 3]` with `valueDiff = 6` reports a spurious hit
  across the 0 boundary. Port this to another language and you must offset the
  values or branch on the sign.
- **Evict exactly one entry per step, by key.** When `i >= indexDiff`, the
  value falling out is `nums[i - indexDiff]`; delete `nums[i - indexDiff] //
  width`, not the current key. The eviction is what enforces the *position*
  constraint, and forgetting it turns the answer into "any pair anywhere".
""",
        ),
        (
            "Dry run",
            """
`nums = [1, 5, 1], indexDiff = 1, valueDiff = 0` → width 1, buckets are values.

- i=0: bucket 1 free → store `{1: 1}`.
- i=1: bucket 5 free; neighbours 4 and 6 absent → store; then `i >= 1`, so
  evict `nums[0] // 1 = 1`. Map is `{5: 5}`.
- i=2: bucket 1 — **empty**, because it was evicted. Answer `False`, correctly:
  the two 1s are three apart in position.

Skip the eviction and this returns `True`.

`nums = [-1, 2147483647], indexDiff = 1, valueDiff = 2147483647` → width 2³¹.
`-1 // 2³¹ = -1`, `2147483647 // 2³¹ = 0`. Adjacent, so it checks
`2147483647 - (-1) = 2147483648 < 2³¹`? No. Answer `False` — the difference is
one larger than the limit. The truncating-division version puts both in bucket
0 and answers `True`.
""",
        ),
        (
            "Follow-ups",
            """
- **`valueDiff = 0`** degenerates to Contains Duplicate II — a plain hash set
  over a sliding window. Worth noticing out loud that the bucket solution
  already *is* that when the width is 1.
- **Longest window instead of a boolean** —
  [LC 1438](../longest-continuous-subarray-with-absolute-diff-less-than-or-equal-to-limit/)
  asks for the longest run with `max - min <= limit`. Bucketing does not help
  there; you need both extremes of the window, which is two monotonic deques.
- **Window by timestamp rather than index** — same structure, evict by time
  instead of by `i - indexDiff`. The bucketing argument is untouched.
""",
        ),
    ],
}


def contains_nearby_almost_duplicate(nums: list[int], index_diff: int, value_diff: int) -> bool:
    """Bucketing: O(n). One value per bucket, three buckets checked per step."""
    if index_diff < 1 or value_diff < 0:
        return False

    width = value_diff + 1
    seen: dict[int, int] = {}  # bucket key -> the single value living in it

    for i, value in enumerate(nums):
        key = value // width  # floor division: -1 // 7 == -1, never 0

        if key in seen:
            return True  # same bucket => difference <= value_diff, no test needed
        if key - 1 in seen and value - seen[key - 1] < width:
            return True
        if key + 1 in seen and seen[key + 1] - value < width:
            return True

        seen[key] = value
        if i >= index_diff:
            del seen[nums[i - index_diff] // width]  # the position constraint

    return False


def contains_nearby_almost_duplicate_ordered(
    nums: list[int], index_diff: int, value_diff: int
) -> bool:
    """The ordered-set framing: one ceiling query per step, O(k) insert on a list."""
    if index_diff < 1 or value_diff < 0:
        return False

    window: list[int] = []  # the last index_diff values, sorted

    for i, value in enumerate(nums):
        position = bisect_left(window, value - value_diff)  # ceiling(value - t)
        if position < len(window) and window[position] <= value + value_diff:
            return True

        insort(window, value)
        if i >= index_diff:
            window.pop(bisect_left(window, nums[i - index_diff]))

    return False


CASES = [
    (([1, 2, 3, 1], 3, 0), True),
    (([1, 5, 9, 1, 5, 9], 2, 3), False),
    (([1, 5, 1], 1, 0), False),  # the eviction case
    (([4, 2], 1, 2), True),  # adjacent buckets, exactly at the limit
    (([-1, 2147483647], 1, 2147483647), False),  # floor vs truncating division
    (([-3, 3], 2, 6), True),  # negatives, adjacent buckets
    (([1], 1, 1), False),  # a pair needs two elements
    (([], 3, 3), False),
]


def solve(nums: list[int], index_diff: int, value_diff: int) -> bool:
    return contains_nearby_almost_duplicate(nums, index_diff, value_diff)


def check() -> None:
    for args, expected in CASES:
        assert contains_nearby_almost_duplicate(*args) == expected, args
        # The two solutions must agree on every case, including the sign edges.
        assert contains_nearby_almost_duplicate_ordered(*args) == expected, args
