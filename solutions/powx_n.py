"""Pow(x, n) — LeetCode 50."""

from __future__ import annotations

META = {
    "pattern": "math-geometry",
    "insight": "Read the exponent in binary: square x at every bit position and multiply in only the bits that are set.",
    "time": "O(log |n|)",
    "space": "O(1) iteratively, O(log |n|) if you write it recursively",
    "sections": [
        (
            "What it asks",
            """
Compute `x` raised to the integer power `n`, where `n` is a signed 32-bit
integer — so `n` runs from `-2147483648` to `2147483647` and can be negative.

Two clarifying questions actually change the code:

- **Is `n` an integer?** Yes. Fractional exponents are a completely different
  problem (Newton's method or `exp(n · ln x)`).
- **What is the range of `n`?** The answer `-2³¹ … 2³¹-1` is not trivia — the
  asymmetric lower end is the trap this problem is built around.

And `math.pow` / `**` are off the table by construction; the question is
whether you can implement them.
""",
        ),
        (
            "The loop, and the number that kills it",
            """
`result = 1; for _ in range(n): result *= x`.

`n` can be `2147483647`, so that is **2.1 × 10⁹ multiplications** for a single
call. At a realistic few hundred million floating-point multiplies per second
that is roughly ten seconds — and 2.1 billion roundings compound into an
answer whose low bits are meaningless even if you waited.

The target is O(log n): **31 multiplications**, not two billion. A factor of
about 7 × 10⁷.
""",
        ),
        (
            "The insight",
            """
Write the exponent in binary. `x¹³` with `13 = 1101₂` is

```
x¹³ = x⁸ · x⁴ · x¹
```

and `x¹, x², x⁴, x⁸, …` is just repeated squaring — each one is the previous
one times itself. So walk the bits of `n` from the least significant end,
keeping a running `x` that doubles its exponent each step, and fold it into
the result whenever the current bit is set:

```
while n:
    if n & 1:
        result *= x
    x *= x
    n >>= 1
```

`n` halves each turn, so the loop runs `⌊log₂ n⌋ + 1` times: **31 iterations**
at the top of the 32-bit range.

The recursive phrasing (`half = pow(x, n // 2); return half * half` plus one
extra `x` when `n` is odd) is the same algorithm and reads more clearly, but
costs O(log n) stack. Both are accepted; the iterative one is the one to write
when the follow-up is "now do it modularly for a crypto-sized exponent".
""",
        ),
        (
            "The negative exponent trap",
            """
Handle `n < 0` by inverting: `x = 1 / x; n = -n`.

That line is where the interview turns. **`-(-2147483648)` is `2147483648`,
which does not fit in a signed 32-bit int.** In Java or C++ that negation
overflows and silently wraps straight back to `-2147483648`, the loop condition
`n > 0` is false immediately, and you return `1.0` for every input. The test
suite has that case.

The fixes, in order of preference:

1. Widen the exponent to 64 bits (`long n`) **before** negating. One word of
   code, no case analysis. In Python this is free — ints are unbounded — but
   say it anyway, because the interviewer is checking whether you *noticed*.
2. Peel one factor off first: `if n < 0: x = 1/x; result = x; n = -(n + 1)`.
   Now the negation is of `-2147483647`, which is representable.

A second, quieter decision: invert `x` **once** at the start rather than
inverting the result at the end. Both are one division, but inverting first
keeps every intermediate in the same magnitude regime, and if `|x| > 1` and
`n` is very negative, squaring the un-inverted `x` runs to infinity before you
ever divide.
""",
        ),
        (
            "Dry run",
            """
`x = 2.0, n = 10`. Binary `1010₂`.

| n | bit | result before | x |
|---|---|---|---|
| 10 | 0 | 1 | 2 |
| 5 | 1 | 1 → 4 | 4 |
| 2 | 0 | 4 | 16 |
| 1 | 1 | 4 → 1024 | 256 |
| 0 | — | 1024 | — |

Four iterations, two multiplications into `result`. `2¹⁰ = 1024`. The naive
loop would have done ten.

Now `x = 2.0, n = -2`: invert to `x = 0.5, n = 2`. Bits `10₂` → `result` picks
up `0.5² = 0.25`. Correct.
""",
        ),
        (
            "Follow-ups",
            """
- **Modular exponentiation** — the identical loop with `% mod` after each
  multiply. This is RSA, this is `pow(a, b, m)`, and it is the version that
  actually appears in production. Interviewers often ask for it as the
  immediate follow-up: *Super Pow* (372) and *Count Good Numbers* (1922) are
  both this loop.
- **Matrix power** — replace scalar multiply with 2×2 matrix multiply and you
  get the O(log n) Fibonacci. Same skeleton, different monoid; that framing
  ("any associative operation") is the right thing to say.
- **Floating-point accuracy** — repeated squaring performs O(log n) roundings
  instead of O(n), so it is *more* accurate than the naive loop, not less.
  Worth stating, because people assume the clever version is sloppier.
- **Overflow the other way** — `x = 2.0, n = 2³¹` overflows a double to
  infinity long before the loop ends. The problem constrains `|x| ≤ 100` and
  bounds the answer, but ask whether saturating or raising is wanted.
""",
        ),
    ],
}


def my_pow(x: float, n: int) -> float:
    if n < 0:
        # Invert first, not last: keeps intermediates from running to infinity.
        # In a 32-bit language, widen n to 64 bits before this negation.
        x = 1 / x
        n = -n

    result = 1.0
    while n:
        if n & 1:  # this bit of the exponent is set
            result *= x
        x *= x  # x, x², x⁴, x⁸, ...
        n >>= 1

    return result


CASES = [
    ((2.0, 10), 1024.0),
    ((2.0, 0), 1.0),
    ((2.0, 1), 2.0),
    ((2.0, -2), 0.25),
    ((-2.0, 3), -8.0),
    ((-2.0, 4), 16.0),
    ((0.5, -3), 8.0),
    ((1.0, -2147483648), 1.0),
    ((-1.0, -2147483648), 1.0),
    ((3.0, 5), 243.0),
]


def solve(x: float, n: int) -> float:
    return my_pow(x, n)
