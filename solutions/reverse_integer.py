"""Reverse Integer — LeetCode 7."""

from __future__ import annotations

INT_MIN = -(2**31)
INT_MAX = 2**31 - 1

META = {
    "pattern": "math-geometry",
    "insight": "The problem is not the reversal, it is detecting 32-bit overflow before it happens — check the last digit against 214748364.",
    "time": "O(log₁₀ x)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Reverse the digits of a signed 32-bit integer. If the reversed value falls
outside `[-2³¹, 2³¹ - 1]`, return `0`.

The reversal is trivial. The **entire** question is the overflow rule, and in
Python that rule has to be written by hand, because ints are arbitrary
precision and nothing will overflow on its own. Say this out loud — an
interviewer watching you compute `int(str(x)[::-1])` and return it wants to
know whether you understand that you are simulating a 32-bit machine.
""",
        ),
        (
            "The insight",
            """
Build the answer digit by digit with `result = result * 10 + digit`, and check
**before** each step that the step will not overflow. In a language where the
overflow is real you cannot check afterwards — the value is already wrapped.

Working on the magnitude keeps one bound instead of two. With
`limit = 2³¹ - 1 = 2147483647`:

```
if result > limit // 10:                      overflow for any digit
if result == limit // 10 and digit > 7:       overflow for this digit
```

`limit // 10` is `214748364`. Once `result` has reached it, one more digit is
one too many unless that digit is small enough.

Three details decide correctness:

- **Sign first, digits after.** Python's `%` and `//` round toward negative
  infinity, so `-123 % 10` is `7`, not `3`. Strip the sign with `abs`, reverse
  the magnitude, reapply the sign. In C or Java truncation goes the other way
  and the naive loop happens to work — which is exactly why the habit of
  reversing `abs(x)` is the safe one to carry between languages.
- **`-2³¹` has no positive counterpart.** `abs(-2147483648)` is `2147483648`,
  which is one past `INT_MAX`. It is fine here — its reversal `8463847412` is
  far past the limit and gets rejected — but in a language with real 32-bit
  ints, `abs(INT_MIN)` is undefined behaviour. Reverse into a wider type or
  work in the negative direction.
- **Trailing zeros vanish.** `120` reverses to `21`, not `021`. Falls out of
  the arithmetic for free; do not "fix" it.
""",
        ),
        (
            "Follow-ups",
            """
- **"Do it without a loop guard — detect after the fact."** Compute
  `result = result * 10 + digit`, then check `(result - digit) // 10 != previous`.
  It works, but only in a language that wraps predictably; on signed overflow
  in C++ it is undefined behaviour, so the pre-check is the answer that
  survives scrutiny.
- **String Reverse / Atoi (LeetCode 8)** is the same overflow clamp attached
  to a parser, and there the out-of-range answer is *clamped* to `INT_MAX` or
  `INT_MIN` rather than zeroed. Read which one the problem wants; the two
  problems sit next to each other and the rules differ.
- **Reverse Bits (190)** looks like a sibling but is pure shifting — no
  overflow question at all, because the width is fixed by construction.
""",
        ),
    ],
}


def reverse(x: int) -> int:
    sign = -1 if x < 0 else 1
    remaining = abs(x)  # sign stripped: Python's % rounds toward -inf
    result = 0

    while remaining:
        digit = remaining % 10
        remaining //= 10

        # Check before multiplying: in a fixed-width language it is too late after.
        if result > INT_MAX // 10 or (result == INT_MAX // 10 and digit > 7):
            return 0
        result = result * 10 + digit

    result *= sign
    return result if INT_MIN <= result <= INT_MAX else 0


CASES = [
    ((123,), 321),
    ((-123,), -321),
    ((120,), 21),
    ((0,), 0),
    ((1534236469,), 0),
    ((-2147483648,), 0),
    ((1463847412,), 2147483641),
    ((-1463847412,), -2147483641),
    ((7,), 7),
]


def solve(x: int) -> int:
    return reverse(x)
