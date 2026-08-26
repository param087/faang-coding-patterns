"""Total Hamming Distance — LeetCode 477."""

from __future__ import annotations

META = {
    "pattern": "bit-manipulation",
    "insight": "Sum over bit columns instead of over pairs: a column with k ones and n-k zeros contributes exactly k*(n-k).",
    "time": "O(32n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
The Hamming distance between two integers is the number of bit positions where
they differ. Return the sum of that distance over **all pairs** in the array.

Worth asking: are the values non-negative? LeetCode says `0 <= nums[i] < 2^31`,
which is what lets you loop a fixed 32 columns and skip any two's-complement
argument. If negatives were allowed you would fix a width and mask, but the
counting is identical.
""",
        ),
        (
            "The insight",
            """
The pair loop is O(n²) — at n = 10⁴ that is 5·10⁷ `popcount` calls, and the
constraints go there deliberately.

Flip the nesting. Distance is a **sum over bit positions**, and summation
commutes: instead of "for each pair, count differing bits", do "for each bit,
count differing pairs". A single bit column is just a list of 0s and 1s, and two
entries differ in that column exactly when one is a 1 and the other a 0. With
`k` ones and `n - k` zeros the column contributes `k * (n - k)` — no pair
enumeration at all.

```
[4, 14, 2]  ->  00100
                01110
                00010

bit 1: two ones, one zero -> 2 * 1 = 2
bit 2: two ones, one zero -> 2 * 1 = 2
bit 3: one one,  two zeros -> 1 * 2 = 2
                                    total 6
```

That is 32 passes of O(n) regardless of n, so 10⁴ elements is 3·10⁵ operations
rather than 5·10⁷. The whole trick is recognising that the bit columns are
independent — nothing about one column constrains another.
""",
        ),
        (
            "Edge cases",
            """
- **Empty array and single element** — zero pairs, answer 0. The formula gives
  it for free: `k * (n - k)` is 0 when `n <= 1`.
- **All equal** — every column is all-ones or all-zeros, so every term is
  `k * 0` or `0 * (n - k)`. Answer 0.
- **Overflow** — not in Python, but flag it: with n = 10⁴ the total can reach
  `32 * (5000)² = 8·10⁸`, which fits in a 32-bit signed int, though only just.
  In Java you would still reach for `int` here, but check the arithmetic first.
- **The counting mistake worth naming**: `k * (n - k)` counts each unordered
  pair once. Writing `2 * k * (n - k)` (or summing over ordered pairs) doubles
  the answer, and every test case where it matters will be off by exactly 2×.
""",
        ),
    ],
}


def total_hamming_distance(nums: list[int]) -> int:
    n = len(nums)
    total = 0

    for bit in range(32):
        ones = sum(1 for value in nums if value >> bit & 1)
        total += ones * (n - ones)  # unordered pairs straddling this column

    return total


CASES = [
    (([4, 14, 2],), 6),
    (([4, 14, 4],), 4),
    (([],), 0),
    (([5],), 0),
    (([0, 0, 0],), 0),
    (([1, 2, 4, 8],), 12),
    (([0, 2147483647],), 31),
]


def solve(nums: list[int]) -> int:
    return total_hamming_distance(nums)
