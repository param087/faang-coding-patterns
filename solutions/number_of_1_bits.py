"""Number of 1 Bits — LeetCode 191."""

from __future__ import annotations

META = {
    "pattern": "bit-manipulation",
    "insight": "n & (n - 1) clears the lowest set bit, so the loop runs once per 1 rather than once per bit position.",
    "time": "O(k) where k is the number of set bits — at most 32",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Return the Hamming weight — the number of set bits — of a 32-bit word.

Two clarifying questions actually change the code:

1. **Is a built-in allowed?** `bin(n).count("1")`, `int.bit_count()`,
   `Integer.bitCount`, `__builtin_popcount` all solve it. Ask, then write the
   real loop anyway, because the interviewer wants to see `n & (n - 1)`.
2. **Is the input treated as unsigned?** LeetCode's original signature was an
   *unsigned* 32-bit integer. That matters enormously in Python, where there
   is no such thing — see the last section.
""",
        ),
        (
            "The insight",
            """
The obvious loop tests each of the 32 positions:

```python
while n:
    count += n & 1
    n >>= 1
```

Correct, and always 32 iterations for a value with a high bit set.

Brian Kernighan's trick does better. **`n & (n - 1)` clears the lowest set
bit** and nothing else:

```
n      = 1011 0100
n - 1  = 1011 0011   (the lowest 1 becomes 0, everything below it becomes 1)
n & .. = 1011 0000
```

Subtracting 1 borrows through the trailing zeros, flipping them to 1s and
turning the lowest 1 into a 0; the AND then keeps only the bits above it. So
each iteration removes exactly one 1, and the loop runs **popcount times, not
32 times**. For a sparse word like `1 << 31` that is one iteration instead of
thirty-two.

That same expression is the whole of [Power of Two](../power-of-two/) and the
alternative recurrence in [Counting Bits](../counting-bits/). It is worth
knowing cold.
""",
        ),
        (
            "The trap: Python has no 32-bit int",
            """
Python integers are arbitrary precision and behave as if two's complement
extends infinitely to the left. So a negative input has **infinitely many
leading 1s**, and Kernighan's loop does not just give a wrong answer — it
never terminates:

```
-1 & -2 = -2,  -2 & -3 = -4,  -4 & -5 = -8,  ...
```

It marches towards negative infinity forever. Same for `while n: n >>= 1`,
since `-1 >> 1` is `-1`.

Fix it by pinning the width before you start: `n &= 0xFFFFFFFF`. That is what
the code below does, so `-1` correctly reports 32 set bits, matching what a
Java or C++ solution sees for the same word.

The equivalent language traps:

- **Java**: use `n >>>= 1` (logical shift), never `n >>= 1`, or `-1` loops
  forever there too.
- **C**: cast to `unsigned` before shifting; right-shifting a negative signed
  int is implementation-defined.

**Follow-up — "called a million times?"** Precompute a 256-entry byte table
and do four lookups per word, or use the SWAR popcount with the
`0x55555555 / 0x33333333 / 0x0F0F0F0F` masks, which is branch-free and
constant time regardless of how many bits are set.
""",
        ),
    ],
}

MASK32 = 0xFFFFFFFF


def hamming_weight(n: int) -> int:
    n &= MASK32  # pin the width; Python ints are otherwise infinite

    count = 0
    while n:
        n &= n - 1  # clear the lowest set bit
        count += 1

    return count


CASES = [
    ((11,), 3),  # 1011
    ((128,), 1),  # a single high bit: one iteration, not eight
    ((2147483645,), 30),
    ((0,), 0),
    ((1,), 1),
    ((4294967295,), 32),  # all ones
    ((-1,), 32),  # the same word, read as signed — no infinite loop
    ((-2147483648,), 1),  # INT_MIN is one set bit
]


def solve(n: int) -> int:
    return hamming_weight(n)
