"""Palindrome Number — LeetCode 9."""

from __future__ import annotations

META = {
    "pattern": "math-geometry",
    "insight": "Reverse only the back half and stop when it meets the front half — no string, and nothing can overflow.",
    "time": "O(log₁₀ n) — one pass over the digits, and only half of them",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Is the integer `x` the same read forwards and backwards?

The interesting version is the one the problem hints at: **without converting
to a string**. `str(x) == str(x)[::-1]` is a one-liner and it is correct, but
if you offer it you should immediately say "the no-string version is this" —
otherwise the question has told the interviewer nothing.

Worth asking: are negatives palindromes? The problem says no, because of the
leading minus. State that assumption rather than discovering it in a test.
""",
        ),
        (
            "The insight",
            """
The obvious no-string answer reverses the whole number and compares. That
works in Python but **overflows in Java or C++**: `x` can be near `2³¹ - 1`
and its reversal need not fit in 32 bits. The interviewer is fishing for this.

Reverse only the **back half**:

```
while x > reversed_half:
    reversed_half = reversed_half * 10 + x % 10
    x //= 10
```

`x` shrinks by a digit each turn and `reversed_half` grows by one, so the loop
ends exactly when they cross in the middle. Neither value ever exceeds the
original, so overflow is structurally impossible.

At the exit there are two shapes:

- **even digit count** — `1221` becomes `x = 12`, `reversed_half = 12`;
- **odd digit count** — `12321` becomes `x = 12`, `reversed_half = 123`, and
  the middle digit is irrelevant, so drop it with `reversed_half // 10`.
""",
        ),
        (
            "Edge cases",
            """
- **Negatives** — `-121` reversed is `121-`. Reject up front.
- **Trailing zero** — any `x` ending in `0` (other than `0` itself) would need
  a leading zero to match, so it cannot be a palindrome. This guard is not
  cosmetic: drop it and `10` returns **`True`**. Trace it — the loop leaves
  `x = 0` and `reversed_half = 1`, and the odd-length branch tests
  `0 == 1 // 10`, which is `0 == 0`. Same for `100`, `1000`, and every other
  power of ten. This is the single most common wrong submission.
- **Single digit** — `0` through `9` are all palindromes; the loop body never
  runs and `x == reversed_half` is `x == 0` only for `0`, so the odd-length
  branch `x == reversed_half // 10` is what saves `7`. Check it.
""",
        ),
    ],
}


def is_palindrome(x: int) -> bool:
    # Negatives never are; a trailing zero would need a leading zero to match.
    if x < 0 or (x % 10 == 0 and x != 0):
        return False

    reversed_half = 0
    while x > reversed_half:  # meets in the middle, so nothing overflows
        reversed_half = reversed_half * 10 + x % 10
        x //= 10

    # Even length: they are equal. Odd length: drop the shared middle digit.
    return x == reversed_half or x == reversed_half // 10


CASES = [
    ((121,), True),
    ((-121,), False),
    ((10,), False),
    ((0,), True),
    ((7,), True),
    ((1221,), True),
    ((1000021,), False),
    ((2147447412,), True),
]


def solve(x: int) -> bool:
    return is_palindrome(x)
