"""Median of Two Sorted Arrays — LeetCode 4."""

from __future__ import annotations

from math import inf

META = {
    "pattern": "binary-search",
    "insight": "Do not search for the median value — search for the cut that puts half of everything on the left, and binary search only the shorter array.",
    "time": "O(log min(m, n))",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Two sorted arrays. Return the median of their union, as a float — the middle
element when the total length is odd, the mean of the middle two when it is
even. The problem **states** O(log(m + n)), which is the entire difficulty.

Clarify three things first, because each changes the code:

- Either array may be **empty** (only one of them, since m + n ≥ 1). Your
  index arithmetic has to survive that without a special case.
- Values may **repeat**, and may be negative. Sentinels of 0 or −1 are wrong.
- The answer is a float with a possible `.5`, not a truncated integer.
""",
        ),
        (
            "Merge, and why it is not the answer",
            """
Merge the two arrays and index the middle: O(m + n) time, O(m + n) space. Keep
two pointers instead and walk only to the midpoint: still O(m + n) time, now
O(1) space. Both are easy, both are correct, and at m = n = 1000 both cost
about 2000 steps — a microsecond.

So performance is not the reason to move on; the **stated requirement** is.
This is one of the few problems where the naive solution is fast enough in
practice and still fails the interview, because the question is explicitly
"can you get to log?" Write the merge in one sentence, name its complexity,
then go to the real solution rather than typing it out.
""",
        ),
        (
            "The insight",
            """
Stop looking for a *value*. Look for a **cut**.

Split each array into a left part and a right part:

```
nums1:  a[0..i-1] | a[i..]
nums2:  b[0..j-1] | b[j..]
```

If the combined left part has exactly ⌈(m + n) / 2⌉ elements **and** every
element on the left is ≤ every element on the right, then the cut is the
median line. The answer reads straight off the four elements next to it — no
merging, no counting.

Two facts make it a binary search:

1. Once you choose `i`, `j` is **forced**: `j = half - i`. One unknown, not
   two.
2. Validity is monotone in `i`. Take one more element from `nums1` and the
   left part's largest can only grow while the right part's smallest can only
   shrink. So `a[i-1] > b[j]` means `i` is too big, `b[j-1] > a[i]` means it
   is too small, and you halve the range of `i` on each check.

Search `i` over `[0, m]` — the endpoints matter, since taking **none** or
**all** of an array is a legal cut.
""",
        ),
        (
            "The three details that decide it",
            """
**Search the shorter array.** Swap so `m <= n` up front. Otherwise `j` can
fall outside `[0, n]` and you need bounds patches everywhere. It also drops
the complexity to O(log min(m, n)) — with a 10-element array against a
10-million-element one, that is 4 probes instead of 24.

**Use ±∞ sentinels, not index guards.**

```
left1  = nums1[i - 1] if i > 0 else -inf
right1 = nums1[i]     if i < m else  inf
```

An empty left part behaves as if it held −∞ (never blocks the ≤ test) and an
empty right part as if it held +∞. This is what makes an empty input array,
and a cut at either end, need no special case at all. Writing the four
`if`s by hand instead is where this problem is usually lost.

**`half = (m + n + 1) // 2`, with the `+ 1`.** That puts the extra element on
the **left** when the total is odd, so the odd answer is just
`max(left1, left2)` — the same two variables the even case already needs. Drop
the `+ 1` and the odd case needs a separate lookup on the right.
""",
        ),
        (
            "Dry run",
            """
`nums1 = [1, 3, 8, 9, 15]` (m = 5), `nums2 = [7, 11, 18, 19, 21, 25]` (n = 6).
Total 11, odd. `half = 6`. Search `i` in `[0, 5]`.

- `i = 2`, so `j = 4`. `left1 = 3`, `right1 = 8`, `left2 = 19`, `right2 = 21`.
  Check: `left2 = 19 > right1 = 8` — too many elements taken from `nums2`, so
  take more from `nums1`: `low = 3`.
- `i = 4`, so `j = 2`. `left1 = 9`, `right1 = 15`, `left2 = 11`,
  `right2 = 18`. Now `9 <= 18` and `11 <= 15` — **valid cut**.
- Odd total → `max(left1, left2) = max(9, 11) = 11`.

The merged array is `1 3 7 8 9 | 11 | 15 18 19 21 25`, and the 6th of 11
elements is indeed 11 — found in two probes, having never merged anything.
""",
        ),
        (
            "Follow-ups",
            """
- **k-th smallest of two sorted arrays.** The same partition with
  `half = k`, or the recursive version that compares `a[k/2 - 1]` with
  `b[k/2 - 1]` and discards `k/2` elements per step. Ask which the interviewer
  wants; the partition generalises better.
- **Median of k sorted arrays.** The partition argument does not extend past
  two. Binary search on the *value* instead — pick a candidate, count how many
  elements are ≤ it with one binary search per array: O(k log n log range).
- **Streaming median**, where elements arrive one at a time: a different
  problem entirely, solved with two heaps (Find Median from Data Stream).
- **Arrays too large for memory**, on disk or across shards: the partition
  version does O(log min(m, n)) random reads and never scans, which is exactly
  why it is worth knowing beyond the interview.
""",
        ),
    ],
}


def find_median_sorted_arrays(nums1: list[int], nums2: list[int]) -> float:
    if len(nums1) > len(nums2):  # always binary search the shorter array
        nums1, nums2 = nums2, nums1

    m, n = len(nums1), len(nums2)
    if n == 0:
        raise ValueError("at least one array must be non-empty")

    half = (m + n + 1) // 2  # size of the combined left part; +1 favours the left
    low, high = 0, m  # how many of nums1 land on the left; both ends are legal

    while low <= high:
        i = (low + high) // 2
        j = half - i  # forced once i is chosen

        left1 = nums1[i - 1] if i > 0 else -inf
        right1 = nums1[i] if i < m else inf
        left2 = nums2[j - 1] if j > 0 else -inf
        right2 = nums2[j] if j < n else inf

        if left1 <= right2 and left2 <= right1:  # valid cut
            if (m + n) % 2:
                return float(max(left1, left2))
            return (max(left1, left2) + min(right1, right2)) / 2

        if left1 > right2:
            high = i - 1  # took too much from nums1
        else:
            low = i + 1  # took too little

    raise ValueError("inputs are not sorted")  # unreachable for sorted input


CASES = [
    (([1, 3], [2]), 2.0),
    (([1, 2], [3, 4]), 2.5),
    (([], [1]), 1.0),
    (([], [2, 3]), 2.5),
    (([1, 2, 3, 4, 5], [6, 7, 8]), 4.5),
    (([-5, -3, -1], [-2, 0]), -2.0),
    (([3], [1, 2, 4, 5, 6]), 3.5),
    (([1, 1, 1], [1, 1]), 1.0),
]


def solve(nums1: list[int], nums2: list[int]) -> float:
    return find_median_sorted_arrays(nums1, nums2)
