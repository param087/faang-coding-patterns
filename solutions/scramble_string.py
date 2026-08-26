"""Scramble String — LeetCode 87."""

from __future__ import annotations

from collections import Counter
from functools import cache

META = {
    "pattern": "dp-strings",
    "insight": "Both halves stay contiguous under any scramble, so the only unknowns are the split point and whether it was swapped.",
    "time": "O(n⁴) — O(n³) states × O(n) split points",
    "space": "O(n³)",
    "sections": [
        (
            "What it asks",
            """
A scramble is built by recursively cutting a string into two non-empty pieces
and optionally swapping them, then scrambling each piece the same way. Decide
whether `s2` is a scramble of `s1`.

Ask: are the cuts binary and the recursion applied to *both* pieces
independently (yes — arbitrary permutations are not allowed); may a piece be
left un-cut at any level (yes, that is the base case); are the lengths equal
(they are, but check anyway and return `False` otherwise).

The trap is treating this as "is `s2` an anagram of `s1`". `"abcde"` and
`"caebd"` are anagrams and the answer is **False** — the binary-tree structure
constrains far more than the multiset does.
""",
        ),
        (
            "The insight",
            """
Whatever the scramble did, the *top* cut split `s1` into a prefix and a suffix,
and those two blocks stayed contiguous in `s2` — either in the same order or
swapped. That is the entire search space: `n - 1` split points, two
orientations each.

For a split of length `k` out of `length`:

- **no swap** — `s1[i : i+k]` must scramble to `s2[j : j+k]`, and the two
  remainders `s1[i+k : ...]` to `s2[j+k : ...]`
- **swapped** — `s1[i : i+k]` must match the *last* `k` characters of the `s2`
  window, i.e. `s2[j + length - k : ...]`, and the remainder matches the front

Getting the swapped offset right is where hand-written solutions go wrong; write
`j + length - k`, not `j + k`.

State is `(i, j, length)` — a start in each string plus a shared length, so
O(n³) states, each doing O(n) work. `@cache` on the recursion turns the
exponential tree into a table. A bottom-up version indexed the same way is
identical work and worth mentioning; top-down wins here because the pruning
below skips whole subtrees that a table would still fill in.
""",
        ),
        (
            "The pruning is not an optimisation",
            """
Two guards, in this order:

1. **Equal windows return True immediately** — a piece is always a scramble of
   itself (zero cuts).
2. **Different character multisets return False immediately.**

Without guard 2 the recursion still terminates, but it explores every split of
every mismatched window. Guard 2 is what makes `n = 30` finish: it kills a
branch in O(length) instead of O(length⁴) below it. Present it as part of the
algorithm, not as a micro-optimisation, because on the hard cases (long strings
of `a`s and `b`s that are anagrams at the top but not below) it is the
difference between milliseconds and a timeout.

Edge cases: unequal lengths → `False`; empty strings → `True`; a single
character matches only itself. And note the split must be **non-empty on both
sides** (`k` ranges over `1 .. length-1`), or the recursion never shrinks and
you get infinite descent.
""",
        ),
    ],
}


def is_scramble(s1: str, s2: str) -> bool:
    if len(s1) != len(s2):
        return False

    @cache
    def scrambles(i: int, j: int, length: int) -> bool:
        left, right = s1[i : i + length], s2[j : j + length]
        if left == right:  # identical window: zero cuts needed
            return True
        if Counter(left) != Counter(right):  # the pruning that makes n=30 finish
            return False

        for k in range(1, length):  # both sides must be non-empty
            # kept in order
            if scrambles(i, j, k) and scrambles(i + k, j + k, length - k):
                return True
            # swapped: the k-prefix of s1 lands at the END of the s2 window
            if scrambles(i, j + length - k, k) and scrambles(i + k, j, length - k):
                return True
        return False

    # The cache is rebuilt per call, so `solve` stays pure across repeated runs.
    return scrambles(0, 0, len(s1))


CASES = [
    (("great", "rgeat"), True),
    (("abcde", "caebd"), False),
    (("abcd", "cdab"), True),
    (("abcd", "bdac"), False),
    (("abcdd", "dbcad"), True),
    (("aabb", "bbaa"), True),
    (("aa", "ab"), False),
    (("a", "a"), True),
    (("", ""), True),
]


def solve(s1: str, s2: str) -> bool:
    return is_scramble(s1, s2)
