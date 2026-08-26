"""Top K Frequent Elements — LeetCode 347."""

from __future__ import annotations

from collections import Counter

META = {
    "pattern": "arrays-hashing",
    "insight": "No frequency can exceed n, so index buckets by count and walk them downwards — counting sort, not a heap.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Return the `k` most frequent values. LeetCode guarantees `k` is at most the
number of distinct values, and that **the answer is unique** — so ties never
straddle the cut-off. Ask about both: without the uniqueness guarantee you must
agree a tie-break rule before writing anything.

The constraint that decides the problem is the explicit one: *better than
O(n log n)*. That single line rules out sorting the frequency table and is the
whole reason the question exists.
""",
        ),
        (
            "The insight",
            """
Counting the frequencies is the easy half. The question is how to pull the top
`k` out of the tally without sorting it.

A frequency is an integer in `1..n`. That is a **small, bounded, integer key** —
the standing invitation to counting sort. Build `n + 1` buckets, put each value
in the bucket indexed by its count, then walk the buckets from `n` down to `1`
and take the first `k` values you meet.

```
nums = [1,1,1,2,2,3]
bucket[1] = [3]
bucket[2] = [2]
bucket[3] = [1]      walk down: 1, then 2  ->  [1, 2]
```

Both passes are O(n), and the bucket array is O(n), so the whole thing is
linear. Size it `n + 1`, not `n`: a single value repeated n times lands in
`bucket[n]`.
""",
        ),
        (
            "Heap, buckets, or quickselect",
            """
The heap answer — push all distinct counts into a size-`k` min-heap — is
**O(n log k)**, and it is the one most people reach for. It is not wrong, and
when `k` is tiny it is genuinely fine. But it does not beat O(n log n) in the
worst case where `k` is close to the number of distinct values, which is what
the constraint asked for. Offer it, then say why you are not writing it.

Quickselect on the (value, count) pairs is **O(n) expected, O(n²) worst case**,
and considerably more code. Buckets get the same expected bound
deterministically. The only argument for quickselect here is that it is O(1)
extra space beyond the counter.

The follow-up to be ready for: **"now the stream is infinite."** Buckets die
immediately — you cannot size an array by `n`. That is where the min-heap comes
back, or a count-min sketch plus a heap if you can accept approximate counts.
""",
        ),
    ],
}


def top_k_frequent(nums: list[int], k: int) -> list[int]:
    counts = Counter(nums)

    # buckets[c] holds every value seen exactly c times; c never exceeds n.
    buckets: list[list[int]] = [[] for _ in range(len(nums) + 1)]
    for value, count in counts.items():
        buckets[count].append(value)

    result: list[int] = []
    for count in range(len(nums), 0, -1):
        for value in buckets[count]:
            if len(result) == k:  # test before appending, so k = 0 works too
                return result
            result.append(value)

    return result


CASES = [
    (([1, 1, 1, 2, 2, 3], 2), [1, 2]),
    (([1], 1), [1]),
    (([4, 4, 4, 4], 1), [4]),  # count == n, so buckets must be sized n + 1
    (([-1, -1, -1, -2, -2, 3, 3, 3, 3], 2), [-1, 3]),
    (([5, 5, 4, 4, 3, 3, 2, 2], 4), [2, 3, 4, 5]),  # every count tied
    (([1, 2, 3, 4, 5], 5), [1, 2, 3, 4, 5]),
    (([7, 7, 8], 0), []),
    (([], 0), []),
]


def solve(nums: list[int], k: int) -> list[int]:
    # Order within a frequency tier is arbitrary; sort so the cases are stable.
    return sorted(top_k_frequent(nums, k))
