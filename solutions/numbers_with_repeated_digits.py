"""Numbers With Repeated Digits — LeetCode 1012."""

from __future__ import annotations

META = {
    "pattern": "dp-advanced",
    "insight": "Count the complement: numbers with all-distinct digits are a permutation count, so answer n minus that.",
    "time": "O(d²) where d = number of digits in n, at most 10",
    "space": "O(d)",
    "sections": [
        (
            "What it asks",
            """
Given `n`, how many integers in `[1, n]` have **at least one repeated digit**.
`n` goes to 10⁹, so enumeration is 10⁹ numbers × 10 digits each — a minute of
CPU at best, and the interviewer is not waiting for it.
""",
        ),
        (
            "The insight",
            """
"At least one repeat" is a horrible thing to count directly. "All digits
distinct" is a **permutation count**, so flip it:

```
answer = n - (count of x in [1, n] with all-distinct digits)
```

Say that sentence first. Everything after it is bookkeeping.

Now count the distinct-digit numbers in two halves.

**Strictly fewer digits than n.** For a length `k < d`, the leading digit has 9
choices (no zero) and the remaining `k - 1` positions are an ordered choice
from the other 9 digits: `9 · P(9, k - 1)`. No comparison against `n` is
needed, because every such number is already smaller.

**Exactly d digits.** Walk the digits of `n` left to right, keeping the set of
digits already fixed. At position `i`, place any digit strictly less than
`n[i]` that is unused (and non-zero if `i = 0`); the remaining `d - i - 1`
positions are then free, giving `P(9 - i, d - i - 1)` each — the pool has
`10 - (i + 1)` digits left.

Then comes the line that decides the problem: if `n[i]` itself is already in
the used set, **stop**. No number that agrees with `n` on this prefix can be
distinct-digit, so there is nothing further to add and nothing further to fix.

If the walk runs to completion without stopping, `n` itself has distinct digits
and has never been counted — add 1. That is exactly what Python's `for/else`
is for.
""",
        ),
        (
            "The three off-by-ones that sink it",
            """
- **The leading zero.** At `i = 0` the inner range starts at 1, not 0. Start it
  at 0 and you count things like `0123` as a four-digit number.
- **Forgetting `n` itself.** `n = 1234` — the walk places smaller digits at
  each position but never places `1234`. Miss the `else` branch and every
  distinct-digit `n` is off by one. Test with `n = 1234` and `n = 1123` to hit
  both sides of the branch.
- **Continuing past a repeat.** After `n = 1101`, position 2 sees `0` — fine —
  but position 1 already saw a second `1`, so the prefix `11` is dead. Adding
  anything for later positions double-counts numbers that cannot exist.

Sanity anchors worth memorising: `n = 20 → 1` (only 11), `n = 100 → 10`,
`n = 1000 → 262`. The last one catches almost every variant of the above,
because `738 = 9 + 81 + 648` and each term is a different bug if wrong.
""",
        ),
    ],
}


def _perm(pool: int, slots: int) -> int:
    """Ordered choices of `slots` items from `pool`: P(pool, slots)."""
    result = 1
    for i in range(slots):
        result *= pool - i
    return result


def _distinct_digit_count(n: int) -> int:
    """How many integers in [1, n] have no repeated digit."""
    if n <= 0:
        return 0

    digits = [int(c) for c in str(n)]
    length = len(digits)
    total = 0

    # Numbers strictly shorter than n: leading digit 1-9, rest from the other 9.
    for k in range(1, length):
        total += 9 * _perm(9, k - 1)

    used: set[int] = set()
    for i, digit in enumerate(digits):
        low = 1 if i == 0 else 0  # no leading zero
        for candidate in range(low, digit):
            if candidate not in used:
                total += _perm(9 - i, length - i - 1)
        if digit in used:
            break  # this prefix already repeats; nothing beyond it survives
        used.add(digit)
    else:
        total += 1  # n itself has all-distinct digits

    return total


def num_dup_digits_at_most_n(n: int) -> int:
    return n - _distinct_digit_count(n)


CASES = [
    ((1,), 0),
    ((10,), 0),
    ((11,), 1),
    ((20,), 1),
    ((100,), 10),
    ((1000,), 262),
    ((1234,), 431),
    ((1123,), 329),
    ((1000000000,), 994388230),
]


def solve(n: int) -> int:
    return num_dup_digits_at_most_n(n)
