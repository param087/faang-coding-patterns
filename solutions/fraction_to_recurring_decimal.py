"""Fraction to Recurring Decimal — LeetCode 166."""

from __future__ import annotations

META = {
    "pattern": "math-geometry",
    "insight": "Long division repeats exactly when a remainder repeats, so map each remainder to the position of the digit it is about to produce.",
    "time": "O(d) — at most d distinct remainders before one repeats",
    "space": "O(d)",
    "sections": [
        (
            "What it asks",
            """
Given numerator and denominator as integers, return the fraction as a decimal
string, wrapping any repeating part in parentheses: `1/2 → "0.5"`,
`2/1 → "2"`, `1/6 → "0.1(6)"`, `4/333 → "0.(012)"`.

This is not a maths problem — floating point is useless here, since `1/3` in a
double is a finite, wrong approximation with no repeat to detect. It is a
**simulate long division and detect a cycle** problem. Say that first; it
reframes everything that follows.

Worth asking: is the denominator guaranteed non-zero (yes, on LeetCode), and
what is the integer range (signed 32-bit, which matters — see the traps).
""",
        ),
        (
            "The insight",
            """
Do the division the way you were taught at school. After the integer part,
each step is:

```
digit, remainder = divmod(remainder * 10, denominator)
```

The state of the process is **entirely** the current remainder. So the moment
a remainder recurs, every digit produced since its last appearance will be
produced again, forever — that is the repeating block, and its start is
exactly where that remainder first appeared.

So keep a dict `remainder → index in the output where its digit will be
written`. When the loop hits a remainder already in the dict, insert `(` at
the recorded index and append `)`.

Two consequences worth stating:

- **Termination is guaranteed.** There are only `d` possible non-zero
  remainders (`1 … d-1`), so within `d` steps you either hit zero (terminating
  decimal) or repeat one. That bounds both the runtime and the output length.
- **The map must store a position, not a digit.** Storing the digit tells you
  a value repeated, not where the cycle began — and `1/6 = 0.1(6)` versus
  `0.(16)` is decided precisely by that distinction.

Build the output as a **list of one-character strings** and `join` at the end.
Concatenating onto a Python string in the loop is O(n²), and you need to
`insert` into the middle anyway, which a string cannot do.
""",
        ),
        (
            "The four traps",
            """
Every wrong submission here is one of these, and none of them is the
algorithm.

**1. Sign.** Compute it *before* taking absolute values, with an XOR on the
two signs — `(num < 0) != (den < 0)` — then work entirely in magnitudes.
Deriving the sign from the quotient fails for `-1/3`, where the integer part
is `0` and carries no sign, so you would emit `0.(3)` instead of `-0.(3)`.

**2. Zero numerator.** `0/-5` must be `"0"`, not `"-0"`. The XOR says
negative; return early before it can.

**3. Truncation direction.** Python's `//` floors toward negative infinity, so
`-7 // 12` is `-1`, not `0`. Working in magnitudes and reattaching the sign
sidesteps this entirely — which is the real reason to do it, beyond tidiness.

**4. `-2³¹ / -1`.** The quotient is `2147483648`, one past `INT_MAX`, and
`abs(-2147483648)` overflows a 32-bit int too. In Python this is free; in Java
or C++ you must widen both operands to `long` before the `abs`. Say it — this
is the same trap as *Reverse Integer* and interviewers reuse it.

And the boundary case that is not a trap but does need a branch: if the
remainder is zero after the integer division, return without a decimal point
at all. `"2"`, not `"2."` and not `"2.0"`.
""",
        ),
    ],
}


def fraction_to_decimal(numerator: int, denominator: int) -> str:
    if numerator == 0:
        return "0"  # before the sign test, so 0/-5 is "0" and not "-0"

    parts: list[str] = []
    if (numerator < 0) != (denominator < 0):  # sign first, then magnitudes
        parts.append("-")

    n, d = abs(numerator), abs(denominator)
    whole, remainder = divmod(n, d)
    parts.append(str(whole))
    if remainder == 0:
        return "".join(parts)  # terminating with no fractional part at all

    parts.append(".")
    seen: dict[int, int] = {}  # remainder -> index in parts of the digit it makes

    while remainder and remainder not in seen:
        seen[remainder] = len(parts)
        digit, remainder = divmod(remainder * 10, d)
        parts.append(str(digit))

    if remainder:  # this remainder already produced a digit: cycle starts there
        parts.insert(seen[remainder], "(")
        parts.append(")")

    return "".join(parts)


CASES = [
    ((1, 2), "0.5"),
    ((2, 1), "2"),
    ((4, 333), "0.(012)"),
    ((1, 6), "0.1(6)"),
    ((7, -12), "-0.58(3)"),
    ((-50, 8), "-6.25"),
    ((0, -5), "0"),
    ((-1, 3), "-0.(3)"),
    ((-2147483648, -1), "2147483648"),
    ((1, 333), "0.(003)"),
]


def solve(numerator: int, denominator: int) -> str:
    return fraction_to_decimal(numerator, denominator)
