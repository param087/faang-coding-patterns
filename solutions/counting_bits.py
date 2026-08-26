"""Counting Bits — LeetCode 338."""

from __future__ import annotations

META = {
    "pattern": "bit-manipulation",
    "insight": "i >> 1 is i with its last bit removed — and that number's popcount is already in the table.",
    "time": "O(n)",
    "space": "O(1) extra, excluding the output",
    "sections": [
        (
            "What it asks",
            """
Return an array where entry `i` is the number of set bits in `i`, for every
`i` from 0 to `n` inclusive.

Ask: is a built-in popcount allowed? (If `bin(i).count('1')` is permitted the
problem is a one-liner, so ask — the interviewer almost certainly wants the
DP.) What is the expected complexity? (O(n), which rules out counting each
number independently.)
""",
        ),
        (
            "The naive answer",
            """
Popcount each number: O(n log n), since each popcount is O(bits).

Correct, and the stated O(n) requirement is telling you it is not the intended
answer.
""",
        ),
        (
            "The insight",
            """
`i >> 1` is `i` with its **last bit removed** — and it is a smaller number,
so its answer is already in the table.

So:

```
bits[i] = bits[i >> 1] + (i & 1)
```

Shift off the low bit, look up the rest, add back whether the low bit was set.
That is a DP over the integers, and it is why this is a DP question rather
than a bit-twiddling one.
""",
        ),
        (
            "Dry run",
            """
0 through 5 → `[0, 1, 1, 2, 1, 2]`.

Check 5 = `101`: `5 >> 1` is `2` = `10`, whose popcount is 1; the low bit of 5
is 1; so `1 + 1 = 2`. ✓
""",
        ),
        (
            "The second recurrence",
            """
Worth offering, because it shows the bit tricks are actually in your hands
rather than memorised:

```
bits[i] = bits[i & (i - 1)] + 1
```

`i & (i - 1)` **clears the lowest set bit**, so the remainder has exactly one
fewer set bit. Same O(n), different route.

That expression also powers Brian Kernighan's popcount, the power-of-two test
(`n & (n-1) == 0`), and the index walk in a
[Fenwick tree](../../patterns/segment-tree/).
""",
        ),
    ],
}


def count_bits(n: int) -> list[int]:
    bits = [0] * (n + 1)

    for i in range(1, n + 1):
        # i >> 1 drops the low bit and is smaller, so it is already computed.
        bits[i] = bits[i >> 1] + (i & 1)

    return bits


def count_bits_kernighan(n: int) -> list[int]:
    """The alternative recurrence: i & (i-1) clears the lowest set bit."""
    bits = [0] * (n + 1)
    for i in range(1, n + 1):
        bits[i] = bits[i & (i - 1)] + 1
    return bits


CASES = [
    ((2,), [0, 1, 1]),
    ((5,), [0, 1, 1, 2, 1, 2]),
    ((0,), [0]),
    ((1,), [0, 1]),
    ((8,), [0, 1, 1, 2, 1, 2, 2, 3, 1]),
]


def solve(n: int) -> list[int]:
    return count_bits(n)


def check() -> None:
    for args, expected in CASES:
        assert count_bits(*args) == expected
        assert count_bits_kernighan(*args) == expected

    # Both must agree with the built-in across a wider range.
    reference = [bin(i).count("1") for i in range(200)]
    assert count_bits(199) == reference
    assert count_bits_kernighan(199) == reference
