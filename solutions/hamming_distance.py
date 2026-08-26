"""Hamming Distance — LeetCode 461."""

from __future__ import annotations

META = {
    "pattern": "bit-manipulation",
    "insight": "XOR marks exactly the positions where two numbers disagree, so the distance is the popcount of x ^ y.",
    "time": "O(k) where k is the number of differing bits — at most 32",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Count the bit positions at which two integers differ.

Ask whether the inputs are non-negative (on LeetCode they are, both below
2³¹) and whether a built-in popcount is allowed. If negatives were in play you
would need to fix a width first, because "how many bits differ" is undefined
without one — the answer for `-1` versus `0` is 32 in a 32-bit word and
infinite in Python's model.
""",
        ),
        (
            "The insight",
            """
Two steps, and the first one is the whole problem:

1. **`x ^ y` is a mask of the disagreements.** XOR gives 1 exactly where the
   bits differ and 0 where they match. Nothing else about `x` and `y` matters
   after this line.
2. **Count the 1s.** Brian Kernighan: `n &= n - 1` clears the lowest set bit,
   so the loop runs once per differing bit rather than 32 times.

```python
return popcount(x ^ y)
```

`bin(x ^ y).count("1")`, `(x ^ y).bit_count()` in Python 3.10+,
`Integer.bitCount(x ^ y)` in Java. Write the explicit loop unless the
interviewer waves it through — the point of the question is that you reach for
XOR without hesitating.
""",
        ),
        (
            "The follow-up that is the real question",
            """
**[Total Hamming Distance](../total-hamming-distance/) (LeetCode 477)**: the
sum of Hamming distances over *all pairs* in an array. Almost everyone reaches
for a double loop, which is O(32n²) — at n = 10⁴ that is **10⁸ pairs**, well
past a time limit.

Flip the axis. Handle **one bit column at a time**: if `k` of the `n` numbers
have that bit set, then `n - k` do not, and every set/unset pairing
contributes exactly 1. So that column contributes

```
k * (n - k)
```

Sum over 32 columns: **O(32n)**, 3·10⁵ operations at the same input size, and
no pair is ever enumerated. That column-wise reframing is the same move as
[Single Number II](../single-number-ii/) and is the transferable idea in this
whole pattern — when bits are independent, stop iterating over elements and
start iterating over positions.

Two smaller ones they may reach for:

- **Hamming distance under a fixed width** with signed inputs — mask with
  `0xFFFFFFFF` before counting, or the Python answer diverges from the Java one.
- **Nearest neighbour in Hamming space**, which is where this stops being a
  toy: bucket by masked prefixes (SimHash / LSH) rather than scanning.
""",
        ),
    ],
}


def hamming_distance(x: int, y: int) -> int:
    diff = x ^ y  # 1 exactly where the two disagree

    distance = 0
    while diff:
        diff &= diff - 1  # clear the lowest set bit
        distance += 1

    return distance


CASES = [
    ((1, 4), 2),  # 0001 vs 0100
    ((3, 1), 1),
    ((0, 0), 0),
    ((5, 5), 0),  # identical inputs
    ((1, 2), 2),
    ((0, 2147483647), 31),  # INT_MAX against zero: every bit but the sign
    ((1024, 0), 1),  # a single high bit, one loop iteration
    ((2863311530, 1431655765), 32),  # 0xAAAAAAAA vs 0x55555555: nothing agrees
]


def solve(x: int, y: int) -> int:
    return hamming_distance(x, y)
