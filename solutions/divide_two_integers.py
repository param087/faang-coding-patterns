"""Divide Two Integers — LeetCode 29."""

from __future__ import annotations

META = {
    "pattern": "bit-manipulation",
    "insight": "Subtract the largest doubling of the divisor that still fits, repeatedly — that is long division in base 2.",
    "time": "O(log² n) — at most 31 outer rounds, each doubling at most 31 times",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Integer-divide `dividend` by `divisor` **without** using multiplication,
division or the modulo operator. Truncate toward zero, and clamp the result to
the signed 32-bit range.

Two clarifications decide the whole answer: truncation is toward **zero**, not
floor (`-7 / 2` is `-3`, not `-4`), and the environment stores only 32-bit
signed integers. The second one exists purely to set up the single overflow
case below.
""",
        ),
        (
            "The insight",
            """
Repeated subtraction is the obvious answer and it is unusable: `2^31 - 1`
divided by 1 is 2·10⁹ subtractions.

Do long division in binary instead. At each round, find the largest `k` with
`divisor << k <= remainder`, subtract that, and add `1 << k` to the quotient.
Doubling is `<< 1`, which is not multiplication, so the constraint holds.

```
93 / 3
  3 -> 6 -> 12 -> 24 -> 48   (96 overshoots)   93 - 48 = 45, quotient += 16
  3 -> 6 -> 12 -> 24         (48 overshoots)   45 - 24 = 21, quotient += 8
  3 -> 6 -> 12               (24 overshoots)   21 - 12 =  9, quotient += 4
  3 -> 6                     (12 overshoots)    9 -  6 =  3, quotient += 2
  3                          ( 6 overshoots)    3 -  3 =  0, quotient += 1
                                               quotient = 31
```

Each outer round at least halves the remainder relative to the divisor, so
there are at most 31 rounds and the whole thing is ~31² shift-compare steps.

Handle the sign once, up front: record whether exactly one operand is negative,
divide the magnitudes, negate at the end. Mixing sign handling into the loop is
where this problem goes wrong under time pressure.
""",
        ),
        (
            "The overflow case, and a language caveat",
            """
`INT_MIN / -1` is `2^31`, which does not fit in a signed 32-bit int. The
problem says return `INT_MAX`. This is the one hard-coded branch and it must
come **first**, before you take any absolute values.

That matters more outside Python than in it. In C++ or Java, `abs(INT_MIN)` is
itself undefined/overflowing, so the idiomatic solution there works entirely in
**negative** space — negate both operands to non-positive, loop with `>=`
comparisons on negatives — precisely so no intermediate ever needs the
magnitude `2^31`. Python's arbitrary-precision ints make `abs(-2**31)` safe, so
the code below can stay in positives, but saying "in Java I would work in
negatives, because `-INT_MIN` overflows" is the answer the interviewer is
listening for.

Other cases worth stating before you write:

- `dividend = 0` — loop never runs, returns 0, sign logic is a no-op.
- `|dividend| < |divisor|` — returns 0, and `-1 / 2` must be `0` and not `-1`,
  which truncation toward zero gives automatically.
- `divisor = 1` or `-1` on a large dividend — the doubling loop climbs to
  `2^30`-ish in 31 steps rather than looping two billion times. This is the case
  that kills naive repeated subtraction.
""",
        ),
    ],
}

INT_MIN = -(2**31)
INT_MAX = 2**31 - 1


def divide(dividend: int, divisor: int) -> int:
    if dividend == INT_MIN and divisor == -1:
        return INT_MAX  # the only result that does not fit

    negative = (dividend < 0) != (divisor < 0)
    remainder, magnitude = abs(dividend), abs(divisor)
    quotient = 0

    while remainder >= magnitude:
        chunk, multiple = magnitude, 1
        while remainder >= chunk << 1:  # largest doubling that still fits
            chunk <<= 1
            multiple <<= 1
        remainder -= chunk
        quotient += multiple

    return -quotient if negative else quotient


CASES = [
    ((10, 3), 3),
    ((7, -3), -2),
    ((-7, 2), -3),
    ((-2147483648, -1), 2147483647),
    ((-2147483648, 1), -2147483648),
    ((2147483647, 1), 2147483647),
    ((0, 5), 0),
    ((-1, 2), 0),
]


def solve(dividend: int, divisor: int) -> int:
    return divide(dividend, divisor)
