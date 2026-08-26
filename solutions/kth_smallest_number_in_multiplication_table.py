"""Kth Smallest Number in Multiplication Table — LeetCode 668."""

from __future__ import annotations

META = {
    "pattern": "binary-search-answer",
    "insight": "Never build the table: counting how many entries are ≤ v takes one pass over the rows, and that count is monotone in v.",
    "time": "O(m log(m·n))",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
In the `m × n` multiplication table (`table[i][j] = i * j`, both 1-indexed),
return the `k`-th smallest value when all `m·n` entries are listed in sorted
order — **with duplicates counted separately**.

That last clause decides the problem. `12` appears as 2×6, 3×4, 4×3 and 6×2,
and each of those occupies its own rank. Candidates who dedupe silently get a
completely different answer and usually do not notice.
""",
        ),
        (
            "The insight",
            """
Materialising the table is O(m·n) = 9·10⁸ cells at the constraint limits
(m, n ≤ 3·10⁴) — far past both time and memory. A min-heap seeded with the
first column and popped `k` times is the standard "kth smallest in a sorted
matrix" move, but `k` runs to 9·10⁸ too, so that is no better.

Binary search on the **value** instead. For a candidate `v`, row `i` contains
the multiples `i, 2i, 3i, …` and the number of them that are `<= v` is exactly
`min(n, v // i)`. So

```
count(v) = sum(min(n, v // i) for i in 1..m)
```

is one pass over `m` rows, no table needed. `count` is non-decreasing, so the
values with `count(v) >= k` form a suffix of `[1, m·n]` and you binary search
its start.

Total work: `m` per check, about 35 checks. At m = 3·10⁴ that is ~10⁶
operations against 9·10⁸.

For a tighter check, iterate rows only up to `min(m, v)`: rows beyond `v`
contribute nothing, and rows below `v // n` contribute a full `n`.
""",
        ),
        (
            "Why the answer is always in the table",
            """
The uneasy part: the search returns the smallest `v` with `count(v) >= k`, and
`v` was never checked for membership in the table. It is in it anyway.

Suppose `v` is not a product. Then `count(v) == count(v − 1)`, because no entry
falls in between — so `v − 1` also satisfies `count >= k`, contradicting `v`
being the smallest such value. The lower-bound search therefore cannot land on
a non-product.

Two more details:

- **`min(n, ...)` is not optional.** Row `i` has only `n` entries; without the
  clamp, row 1 alone reports `v` entries and the count explodes.
- **Search `[1, m*n]`, and return `low`.** The top of the range is the largest
  table entry, so the answer is always inside it.
- **`k = 1` and `k = m*n`** must both work: they land on the two ends of the
  range, which is the fastest way to catch an off-by-one in the loop.
""",
        ),
    ],
}


def find_kth_number(m: int, n: int, k: int) -> int:
    def count_at_most(value: int) -> int:
        # Row i holds i, 2i, ... ni; exactly min(n, value // i) of them are <= value.
        return sum(min(n, value // row) for row in range(1, m + 1))

    low, high = 1, m * n
    while low < high:
        mid = (low + high) // 2
        if count_at_most(mid) >= k:
            high = mid  # enough entries at or below mid; tighten downwards
        else:
            low = mid + 1

    return low


CASES = [
    ((3, 3, 5), 3),
    ((2, 3, 6), 6),
    ((1, 10, 7), 7),
    ((9, 9, 81), 81),
    ((5, 5, 13), 8),
    ((4, 7, 20), 12),
    ((42, 34, 401), 126),
    ((3, 3, 1), 1),
]


def solve(m: int, n: int, k: int) -> int:
    return find_kth_number(m, n, k)
