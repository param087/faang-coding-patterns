"""Nth Magical Number — LeetCode 878."""

from __future__ import annotations

import math

META = {
    "pattern": "binary-search-answer",
    "insight": "Counting magical numbers up to x is O(1) by inclusion-exclusion, and that count is monotone, so binary search x rather than enumerate.",
    "time": "O(log(n · min(a, b)))",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
A number is *magical* if it is divisible by `a` or by `b`. Return the `n`-th
magical number, modulo 10⁹ + 7.

The constraints are the whole story: `n` goes to 10⁹ and `a, b` to 4 × 10⁴, so
the answer can be about 4 × 10¹³. Ask whether `a` and `b` are coprime — they
are not guaranteed to be, which is exactly why the count needs `lcm` and not
`a · b`. Ask whether the answer is wanted modulo something (yes), and note that
this is a hint the true value overflows a 32-bit integer.
""",
        ),
        (
            "The insight",
            """
You cannot walk to the 10⁹-th magical number — that is 10⁹ steps, and a heap
merge of the two arithmetic progressions is no better.

But you can **count** them in O(1). The magical numbers in `[1, x]` are

```
count(x) = x // a  +  x // b  -  x // lcm(a, b)
```

by inclusion–exclusion: the last term removes numbers divisible by both, which
the first two each counted once. `lcm(a, b) = a * b // gcd(a, b)`; using `a * b`
directly double-subtracts whenever the two share a factor, and `a = b = 2` is
enough to expose it.

`count` is non-decreasing in `x`, so `count(x) >= n` is a monotone predicate and
the answer is the **smallest** `x` satisfying it. Standard lower-bound search
over `[min(a, b), n * min(a, b)]`: the low end is the first magical number, and
the high end is achievable because the multiples of the smaller value alone
already supply `n` of them.

That is roughly 46 iterations of O(1) work for a search space of 4 × 10¹³.
""",
        ),
        (
            "The trap: take the modulus last",
            """
Two ways to lose this after getting the algorithm right.

**Reducing inside the loop.** If you apply `% (10**9 + 7)` to `mid`, or search
over a reduced range, the counting function is meaningless — divisibility is
not preserved by the modulus. Binary search over the **true** values, in Python
integers, and reduce only the number you return.

**Landing on a non-magical `x`.** Because the search returns the smallest `x`
with `count(x) >= n`, that `x` is necessarily magical: if it were not, then
`count(x - 1) == count(x) >= n` and `x - 1` would have been feasible, so the
search would never have stopped there. Worth stating out loud, because the
alternative — computing a candidate and then rounding it up to the next
multiple — is a common and unnecessary patch.

Languages with 64-bit integers have a third trap: `n * min(a, b)` is fine at
4 × 10¹³, but `a * b` inside a naive `lcm`, or `mid + high` in a midpoint
computed as `(low + high) / 2`, are the places overflow shows up. Python is
immune; say so rather than pretending the issue does not exist.
""",
        ),
    ],
}

MOD = 10**9 + 7


def nth_magical_number(n: int, a: int, b: int) -> int:
    lcm = math.lcm(a, b)  # a * b overflows the count when gcd(a, b) > 1

    def count(x: int) -> int:
        return x // a + x // b - x // lcm  # inclusion-exclusion

    low, high = min(a, b), n * min(a, b)
    while low < high:
        mid = (low + high) // 2
        if count(mid) >= n:
            high = mid  # feasible; look for something smaller
        else:
            low = mid + 1

    return low % MOD  # reduce only at the very end


CASES = [
    ((1, 2, 3), 2),
    ((2, 2, 3), 3),
    ((4, 2, 3), 6),
    ((5, 2, 4), 10),
    ((3, 6, 4), 8),
    ((10, 3, 3), 30),
    ((1, 1, 1), 1),
    ((1000000000, 40000, 40000), 999720007),
]


def solve(n: int, a: int, b: int) -> int:
    return nth_magical_number(n, a, b)
