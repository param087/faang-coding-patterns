"""Maximum Gap — LeetCode 164."""

from __future__ import annotations

META = {
    "pattern": "sorting",
    "insight": "The largest gap is at least the average gap, so bucket at that width and every within-bucket difference becomes irrelevant.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Return the largest difference between two successive elements once the array is
sorted; zero if it holds fewer than two elements. The catch is the required
complexity: **linear time and linear space**, which rules out sorting and then
scanning.

Say the O(n log n) answer first — sort, one pass of differences — and then say
"but the problem asks for linear, which means either a radix sort or a
pigeonhole argument". That framing is most of the credit.
""",
        ),
        (
            "The insight",
            """
Let `lo` and `hi` be the minimum and maximum, and `n` the count. Sorted, there
are `n - 1` adjacent gaps summing to `hi - lo`, so the **largest** gap is at
least the average:

```
maxGap >= ceil((hi - lo) / (n - 1))
```

Call that lower bound `size` and bucket the values by `(x - lo) // size`. A
bucket spans `size` consecutive integers, so any two values inside one differ by
at most `size - 1`, which is **strictly less than the answer**. The maximum gap
therefore always lies *between* buckets.

So the contents of a bucket never matter — only its minimum and maximum do.
Store two integers per bucket, sweep left to right skipping empty ones, and take
the best `bucket_min[i] - previous_bucket_max`. Two linear passes, `n + 1`
buckets, no comparison sort anywhere.

The trap in the arithmetic: use `size = max(1, (hi - lo) // (n - 1))`. Integer
division floors, which only makes buckets *narrower* than the bound — the
argument still holds — but a `size` of 0 divides by zero when the values are
densely packed.
""",
        ),
        (
            "Edge cases",
            """
- **Fewer than two elements** → 0 by definition. Do this before touching `min`
  or `max`, which raise on an empty list.
- **All elements equal** → `hi == lo`, so `size` collapses; return 0 early. This
  is the case that crashes a solution which only guards on `n < 2`.
- **Empty buckets must be skipped, not treated as zero.** Carrying `previous`
  as "the max of the last non-empty bucket" is what makes the sweep correct;
  comparing against `bucket_max[i - 1]` blindly reads a hole.
- `lo` always lands in bucket 0 and `hi` in the last bucket, so both extremes
  participate — no separate handling.
- **The radix-sort alternative** is also O(n): with 32-bit values, four passes
  of an 8-bit counting sort, then one linear scan of the differences. More code,
  no pigeonhole argument to explain, and it does not fall over on duplicates.
""",
        ),
    ],
}


def maximum_gap(nums: list[int]) -> int:
    n = len(nums)
    if n < 2:
        return 0

    lo, hi = min(nums), max(nums)
    if lo == hi:
        return 0

    # Never wider than the guaranteed lower bound on the answer, never zero.
    size = max(1, (hi - lo) // (n - 1))
    count = (hi - lo) // size + 1

    used = [False] * count
    bucket_min = [0] * count
    bucket_max = [0] * count
    for x in nums:
        b = (x - lo) // size
        if not used[b]:
            used[b] = True
            bucket_min[b] = bucket_max[b] = x
        else:
            bucket_min[b] = min(bucket_min[b], x)
            bucket_max[b] = max(bucket_max[b], x)

    best = 0
    previous = lo  # bucket 0 always holds lo, so this is never a phantom
    for b in range(count):
        if not used[b]:
            continue  # holes are skipped, not compared against
        best = max(best, bucket_min[b] - previous)
        previous = bucket_max[b]
    return best


CASES = [
    (([3, 6, 9, 1],), 3),
    (([15, 3, 7, 1, 10, 9],), 5),
    (([1, 3, 100],), 97),
    (([0, 0, 0, 1],), 1),
    (([1, 10000000],), 9999999),
    (([1, 1, 1, 1],), 0),
    (([10],), 0),
    (([],), 0),
]


def solve(nums: list[int]) -> int:
    return maximum_gap(nums)
