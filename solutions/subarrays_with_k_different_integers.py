"""Subarrays with K Different Integers — LeetCode 992."""

from __future__ import annotations

META = {
    "pattern": "sliding-window",
    "insight": "\"Exactly k\" is not a window invariant; \"at most k\" is — so count exactly(k) as atMost(k) minus atMost(k-1).",
    "time": "O(n)",
    "space": "O(k)",
    "sections": [
        (
            "What it asks",
            """
Count the **subarrays** (contiguous, and counted with multiplicity — two
identical-looking subarrays at different positions are two answers) whose
number of distinct integers is exactly `k`.

Ask: contiguous or subsequence (contiguous)? Count or list them (count — a
list can be exponential)? Are values bounded (LeetCode says `1 <= nums[i] <=
n`, so a hash map is the safe choice either way)?

The word to circle is **exactly**. Everything about this problem follows from
it.
""",
        ),
        (
            "Brute force, and why it fails",
            """
Fix a left end, extend right, maintain a distinct-count incrementally, add one
whenever it equals `k`. Each subarray costs O(1), which sounds fine — but
there are `n(n+1)/2` subarrays.

At n = 2·10⁴ that is roughly **2·10⁸ iterations**. In C++ that is a couple of
seconds and might squeak through; in Python it is minutes, and it is the
wrong answer to give regardless because a linear one exists.
""",
        ),
        (
            "Why the plain window does not work",
            """
The instinct is a single window that maintains "exactly k distinct". Try to
write it and the loop has nowhere to go.

A two-pointer window needs a **monotone** invariant: shrinking from the left
must move you in one predictable direction. "At most k distinct" has that —
removing an element never increases the distinct count, so once valid, always
valid as you shrink. "Exactly k distinct" does not: shrinking can drop you
from k to k-1 and there is no rule saying when to stop, and worse, for a fixed
right end the valid left positions form a *band* in the middle, not a prefix.

So there is no single `left` to track. Recognising that within a minute or two
— rather than fighting the loop for fifteen — is what the problem is testing.
""",
        ),
        (
            "The insight: subtract two windows",
            """
Counting is closed under subtraction even when windows are not:

```
exactly(k) = atMost(k) - atMost(k - 1)
```

Every subarray with at most `k` distinct values either has at most `k-1`, or
has exactly `k`. Subtract and only the second group survives.

`atMost` is the standard window: grow right, and while the map holds more than
`k` keys, drop from the left, deleting keys whose count reaches zero so that
`len(counts)` is an honest distinct-count.

Two linear passes, so still O(n) — and each pass is six lines you already
know. This "difference of two at-most windows" is the reusable move; it also
solves Binary Subarrays With Sum (930) and Count Number of Nice Subarrays
(1248), where the naive framing is likewise not monotone.
""",
        ),
        (
            "The counting line",
            """
```python
total += right - left + 1
```

This is the line to be able to justify. After the window has been repaired,
`[left, right]` is the **longest** valid subarray ending at `right`, and every
suffix of it — starting at `left`, `left+1`, … , `right` — is also valid,
because dropping elements from the front cannot add distinct values. That is
`right - left + 1` new subarrays, all ending at `right`, none counted before.

Summing over every right end counts each subarray exactly once, keyed by its
right end. If you ever find yourself wanting `+= 1` here, you are counting
windows rather than subarrays and will be low by a large factor.

Guard `atMost(-1) = 0` explicitly for `k = 0`; without it the shrink loop
walks `left` past `right` and indexes off the end.
""",
        ),
        (
            "Dry run",
            """
`nums = [1, 2, 1, 2, 3]`, `k = 2`.

`atMost(2)`, adding `right - left + 1` at each step:

| right | window | added | total |
| --- | --- | --- | --- |
| 0 | `[1]` | 1 | 1 |
| 1 | `[1,2]` | 2 | 3 |
| 2 | `[1,2,1]` | 3 | 6 |
| 3 | `[1,2,1,2]` | 4 | 10 |
| 4 | `[2,3]` after shrinking past both 1s | 2 | **12** |

`atMost(1)` never holds more than one value, so it adds 1 at each of the five
positions: **5**.

`12 - 5 = 7`, and the seven are `[1,2] [2,1] [1,2] [1,2,1] [2,1,2] [1,2,1,2]
[2,3]`.

Note step 4: the shrink loop removes *three* elements in one iteration. That
is fine — `left` still only moves forward, so the total work stays linear.
""",
        ),
        (
            "Follow-ups",
            """
- **"One pass instead of two?"** Yes: keep two left pointers, `left_far` for
  the at-most-`k` boundary and `left_near` for the at-most-`k-1` boundary, and
  add `left_near - left_far` at each right end. It is the same arithmetic with
  the subtraction inlined, twice the pointer bookkeeping, and no better
  complexity — offer it as a refinement, do not open with it.
- **Longest subarray with exactly k distinct** — the subtraction trick does
  *not* transfer, because a maximum is not additive. Track, per right end, the
  window boundary where the distinct count last changed.
- **At most k distinct, longest** — LeetCode 340, and just the `atMost` half
  of this file.
- **Same shape, different invariant** — Binary Subarrays With Sum (930) is
  `atMost(sum) - atMost(sum - 1)`; Count Number of Nice Subarrays (1248) is
  the same on odd-parity counts. Once you see one of them you have all three.
""",
        ),
    ],
}


def _at_most(nums: list[int], k: int) -> int:
    """Subarrays containing at most `k` distinct values."""
    if k < 0:
        return 0

    counts: dict[int, int] = {}
    left = 0
    total = 0

    for right, value in enumerate(nums):
        counts[value] = counts.get(value, 0) + 1

        while len(counts) > k:
            leaving = nums[left]
            counts[leaving] -= 1
            if counts[leaving] == 0:
                del counts[leaving]  # keeps len(counts) an honest distinct-count
            left += 1

        # Every suffix of the repaired window is valid too.
        total += right - left + 1

    return total


def subarrays_with_k_distinct(nums: list[int], k: int) -> int:
    return _at_most(nums, k) - _at_most(nums, k - 1)


CASES = [
    (([1, 2, 1, 2, 3], 2), 7),
    (([1, 2, 1, 3, 4], 3), 3),
    (([1, 2, 1, 2, 3], 1), 5),
    (([1, 1, 1, 1], 1), 10),
    (([1, 2, 3], 4), 0),
    (([1], 1), 1),
    (([1], 0), 0),
    (([], 2), 0),
]


def solve(nums: list[int], k: int) -> int:
    return subarrays_with_k_distinct(nums, k)
