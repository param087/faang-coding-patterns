"""Repeated Substring Pattern — LeetCode 459."""

from __future__ import annotations

META = {
    "pattern": "string-algorithms",
    "insight": "A string tiles from a block of length p exactly when p = n - (longest border) divides n, so one prefix-function pass settles it.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Decide whether `s` is some substring repeated two or more times end to end.

Ask whether a single copy counts (no — it must repeat), and whether the block
has to be the *shortest* one (irrelevant to the yes/no answer, but the method
below hands you the shortest for free).
""",
        ),
        (
            "The insight",
            """
Borders and periods are the same fact seen from two ends. If `s` has a border
of length `b` — a proper prefix that is also a suffix — then `s` has period
`p = n - b`, meaning `s[i] == s[i + p]` for every valid `i`.

A period only *tiles* the string when it divides the length. `"aabaaba"` has
period 3 but 7 % 3 != 0, so the last block is cut short and it is not a
repetition. So the whole problem is:

```
p = n - failure[n - 1]
answer = (p < n) and (n % p == 0)
```

`failure[n - 1]` is the last entry of the KMP prefix function — the longest
border of the whole string. Taking the *longest* border gives the *shortest*
period, which is the one most likely to divide `n`; any shorter border gives a
longer period and would miss cases.

`p < n` is the guard that rejects a string with no border at all, where
`p = n` divides `n` trivially and would wrongly report a single copy as a
repetition.
""",
        ),
        (
            "The (s + s)[1:-1] trick, and what it costs",
            """
The famous one-liner: `s in (s + s)[1:-1]`. It works because a non-trivial
rotation of `s` equals `s` precisely when `s` is periodic, and slicing off the
first and last characters forbids the two trivial alignments.

It is a fine answer to *state*, but do not stop there. `in` on Python strings
is a tuned two-way / Crochemore-Perrin search — effectively linear in CPython,
but you are leaning on a library detail, and in an interview asking for
"repeated substring pattern" under the string-algorithms banner the expected
follow-up is *"and if `in` were the naive O(n²) scan?"*. The prefix function
answers that, and it also tells you the block: `s[:p]`.

Concrete separator: `"aabaaba"` (n = 7). Longest border is `"aaba"`, so
p = 3, and 7 % 3 != 0 → **False**, despite a border covering more than half the
string. That is the input that catches "has a long border ⇒ periodic".
""",
        ),
    ],
}


def build_failure(pattern: str) -> list[int]:
    failure = [0] * len(pattern)
    k = 0

    for i in range(1, len(pattern)):
        while k and pattern[i] != pattern[k]:
            k = failure[k - 1]
        if pattern[i] == pattern[k]:
            k += 1
        failure[i] = k

    return failure


def repeated_substring_pattern(s: str) -> bool:
    n = len(s)
    if n < 2:
        return False  # a single character cannot be a repetition of anything

    period = n - build_failure(s)[-1]  # shortest period, from the longest border
    return period < n and n % period == 0


CASES = [
    (("abab",), True),
    (("aba",), False),
    (("abcabcabcabc",), True),
    (("abaababaab",), True),  # period 5, border 5
    (("aabaaba",), False),  # long border, period does not divide n
    (("aabaabaa",), False),
    (("aa",), True),
    (("a",), False),
    (("",), False),
]


def solve(s: str) -> bool:
    return repeated_substring_pattern(s)
