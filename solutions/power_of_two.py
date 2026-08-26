"""Power of Two — LeetCode 231."""

from __future__ import annotations

META = {
    "pattern": "bit-manipulation",
    "insight": "A power of two has exactly one set bit, and n & (n - 1) clears the lowest set bit — so the test is one line plus a positivity guard.",
    "time": "O(1)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Return whether a 32-bit signed integer `n` is a power of two, i.e. whether
`n == 2**x` for some integer `x ≥ 0`.

The input is **signed**, so zero and negatives are legal inputs and both
answer false. The stated follow-up is "without loops or recursion", which is
the whole reason the problem exists — a `while n % 2 == 0` loop is the answer
nobody wants.

Ask whether `1` counts (yes: 2⁰ = 1). Nobody gets this wrong, but asking shows
you noticed the boundary.
""",
        ),
        (
            "The insight",
            """
In binary, powers of two are exactly the values with **one set bit**:
`1`, `10`, `100`, `1000`. So the question is "does `n` have exactly one bit
set?", and `n & (n - 1)` answers it.

Subtracting 1 borrows through the trailing zeros — the lowest 1 becomes 0 and
everything beneath it becomes 1 — so the AND **clears the lowest set bit**:

```
n      = 1000 0000
n - 1  = 0111 1111
n & .. = 0000 0000   →  there was nothing above the lowest 1
```

If the result is zero, `n` had at most one set bit. Combine with `n > 0`:

```python
return n > 0 and n & (n - 1) == 0
```

The sibling identity `n & -n == n` says the same thing — `n & -n` isolates the
lowest set bit, so it equals `n` only when `n` *is* that bit. Either is fine;
`n & (n - 1)` is the one that also gives you
[Number of 1 Bits](../number-of-1-bits/) and
[Counting Bits](../counting-bits/).
""",
        ),
        (
            "Edge cases — the guard is not decoration",
            """
- **n = 0.** `0 & -1 == 0`, so without `n > 0` you return true for zero. This
  is the single most common bug in this problem.
- **n = INT_MIN (−2³¹) in Java or C++.** The bit pattern is `0x80000000` — one
  set bit — and `n - 1` wraps to `0x7FFFFFFF`, so the AND is 0 and you return
  **true for a negative number**. The `n > 0` guard is doing real work, not
  defensive padding. Say this when you write it; interviewers plant negative
  test cases here precisely to see whether the guard was deliberate.
- **n = 1.** True, and `1 & 0 == 0` handles it with no special case.
- **Python has no INT_MIN**, so `-2147483648 & -2147483649` is not `0` there;
  the guard makes the difference invisible, which is exactly what you want.

**The no-loops trick worth knowing:** the largest power of two inside a signed
32-bit int is 2³⁰ = 1 073 741 824, and every smaller power of two divides it,
so `n > 0 and (1 << 30) % n == 0` works too. Cute, but it uses a modulo and
does not generalise past 32 bits — offer it as a second answer, never the
first.

**Follow-up: power of four** (LeetCode 342). One set bit
*and* that bit in an even position: `n > 0 and n & (n - 1) == 0 and
n & 0x55555555 != 0`. The mask `0x5555...` is every even bit position, and it
is the natural next question after this one.
""",
        ),
    ],
}


def is_power_of_two(n: int) -> bool:
    # n > 0 is what rejects 0 and INT_MIN, whose bit patterns look innocent.
    return n > 0 and n & (n - 1) == 0


CASES = [
    ((1,), True),  # 2**0
    ((16,), True),
    ((3,), False),
    ((0,), False),  # the classic missing-guard failure
    ((-16,), False),
    ((-2147483648,), False),  # INT_MIN: one set bit, still not a power of two
    ((1073741824,), True),  # 2**30, the largest that fits in int32
    ((6,), False),
]


def solve(n: int) -> bool:
    return is_power_of_two(n)
