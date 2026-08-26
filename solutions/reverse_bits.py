"""Reverse Bits — LeetCode 190."""

from __future__ import annotations

META = {
    "pattern": "bit-manipulation",
    "insight": "Shift the answer left while shifting the input right: each step pops n's lowest bit and pushes it onto the result's low end.",
    "time": "O(1) — exactly 32 iterations",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Reverse the bits of a 32-bit unsigned integer and return the result as an
unsigned integer.

The clarifying question that actually matters: **is the width fixed at 32?**
It has to be. "Reverse the bits of 1" is meaningless without a width — as a
32-bit word the answer is 2³¹, as an 8-bit word it is 128. Leading zeros are
significant here, which is the one thing that separates this from every other
bit problem in the set.

The other question is LeetCode's own stated follow-up: **is the function
called many times?** That changes the answer from a loop to a lookup table.
""",
        ),
        (
            "The insight",
            """
Treat it as a stack transfer. `n & 1` pops the lowest bit off the input;
`result = (result << 1) | bit` pushes it onto the low end of the output. Do
that 32 times and the first bit you popped — bit 0 — has been shifted left 31
times, landing in position 31. Exactly the reversal.

```python
result = (result << 1) | (n & 1)
n >>= 1
```

No index arithmetic, no `31 - i`, nothing to get off by one. Two lines inside
a `for _ in range(32)`.

In Python you must also mask the result to `0xFFFFFFFF` if you ever want to
feed it back in, since Python will happily let it grow past 32 bits; and in
Java the input arrives as a signed `int`, so you shift with `>>>` and print
the result unsigned.
""",
        ),
        (
            "The early-exit trap, and the O(1) version",
            """
**The trap.** Writing `while n:` instead of `for _ in range(32):` looks like a
free optimisation and is a wrong answer. For `n = 1` the loop runs once,
produces `1`, and stops — but the correct answer is `2³¹`, because those 31
leading zeros of the input must become 31 *trailing* zeros of the output. If
you stop early you must finish with `result <<= (32 - iterations)`. Simpler to
always run 32 times: it is a fixed, tiny cost.

**The follow-up: called many times.** Cache. A word is four bytes, and there
are only 256 distinct bytes, so precompute a 256-entry reversal table and
assemble:

```
rev(n) = T[n & 0xFF] << 24 | T[n >> 8 & 0xFF] << 16
       | T[n >> 16 & 0xFF] << 8 | T[n >> 24]
```

Four lookups instead of thirty-two iterations, with 256 bytes of state.

**The branch-free version**, worth knowing because it shows up in real codecs
— swap halves, then quarters, down to adjacent bits, five steps for 32 bits:

```
n = (n >> 16) | (n << 16)
n = ((n & 0xFF00FF00) >> 8) | ((n & 0x00FF00FF) << 8)
n = ((n & 0xF0F0F0F0) >> 4) | ((n & 0x0F0F0F0F) << 4)
n = ((n & 0xCCCCCCCC) >> 2) | ((n & 0x33333333) << 2)
n = ((n & 0xAAAAAAAA) >> 1) | ((n & 0x55555555) << 1)
```

Each mask pair is "odd group / even group" at that granularity: `AAAA` is
every odd bit, `5555` every even one, `CCCC`/`3333` the same idea for pairs.
Both implementations are in the module and are cross-checked against each
other.
""",
        ),
    ],
}

MASK32 = 0xFFFFFFFF


def reverse_bits(n: int) -> int:
    result = 0

    for _ in range(32):  # always 32 — leading zeros are part of the answer
        result = (result << 1) | (n & 1)
        n >>= 1

    return result


def reverse_bits_masked(n: int) -> int:
    """Branch-free divide and conquer: swap halves, quarters, ... , bits."""
    n &= MASK32
    n = ((n >> 16) | (n << 16)) & MASK32
    n = ((n & 0xFF00FF00) >> 8) | ((n & 0x00FF00FF) << 8)
    n = ((n & 0xF0F0F0F0) >> 4) | ((n & 0x0F0F0F0F) << 4)
    n = ((n & 0xCCCCCCCC) >> 2) | ((n & 0x33333333) << 2)
    n = ((n & 0xAAAAAAAA) >> 1) | ((n & 0x55555555) << 1)
    return n


CASES = [
    ((43261596,), 964176192),
    ((4294967293,), 3221225471),
    ((1,), 2147483648),  # the case that kills `while n:`
    ((2147483648,), 1),
    ((0,), 0),
    ((4294967295,), 4294967295),  # all ones is its own reverse
    ((2863311530,), 1431655765),  # 0xAAAAAAAA -> 0x55555555
]


def solve(n: int) -> int:
    return reverse_bits(n)


def check() -> None:
    for args, expected in CASES:
        assert reverse_bits(*args) == expected
        assert reverse_bits_masked(*args) == expected

    # Both must agree with a string reversal, and reversing twice is identity.
    for n in (0, 1, 7, 12345, 0x0F0F0F0F, 0xDEADBEEF, MASK32):
        expected = int(format(n, "032b")[::-1], 2)
        assert reverse_bits(n) == expected
        assert reverse_bits_masked(n) == expected
        assert reverse_bits(reverse_bits(n)) == n
