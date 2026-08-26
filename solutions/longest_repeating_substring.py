"""Longest Repeating Substring — LeetCode 1062."""

from __future__ import annotations

META = {
    "pattern": "dp-strings",
    "insight": "Run the common-substring table of s against itself, but only above the diagonal, so every cell compares two different end positions.",
    "time": "O(n²)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
This one is premium, so the statement is not public — described in my own
words: given a string `s`, return the length of the longest **contiguous**
substring that occurs at least twice in `s`. Return 0 if no substring repeats.

The clarifying question that decides the answer: **may the two occurrences
overlap?** They may. `"aaaa"` returns **3**, from `s[0..2]` and `s[1..3]`. If
you assume disjoint occurrences you will confidently return 2 and be wrong on
the first test.

Also confirm contiguous, not subsequence — this is the one problem in the
family where the `else` branch is 0 rather than a `max`.
""",
        ),
        (
            "The insight",
            """
Longest common substring of `s` with itself, with the diagonal excluded.

> `dp[i][j]` = the length of the longest common **suffix** of `s[..i]` and
> `s[..j]`, for `i < j`.

```
dp[i][j] = dp[i-1][j-1] + 1   if s[i-1] == s[j-1]
         = 0                  otherwise
```

The reset to 0 is what makes it a substring rather than a subsequence: a
mismatch ends the run, it does not let you skip a character. The answer is the
maximum over the whole table, not the bottom-right cell, because the best run
can end anywhere.

Restricting to `j > i` is what enforces "two occurrences": the two matched runs
end at different positions, so they start at different positions, so they are
two occurrences — while still allowing them to overlap in the middle, which is
exactly the semantics wanted. Comparing `s` to itself without that restriction
returns `n`, the string matching itself.

O(n²) time. At the LeetCode limit n = 2000 that is 4 × 10⁶ cells, comfortably
fine; the rolled row keeps space at O(n).
""",
        ),
        (
            "Overlaps count — and the O(n log n) answer",
            """
Say the overlap rule out loud with `"aaaa"` → 3 as evidence, and keep it as a
test case. It is the only case in the set that separates a correct solution
from a plausible one.

If the interviewer pushes past O(n²) — and at n = 10⁵ they should — the answer
is **binary search on the length plus rolling hash**. Lengths are monotone: if
a repeat of length `L` exists then so does one of length `L-1` (take any
prefix of it). So binary search `L`, and test "is there a repeated substring of
length exactly `L`" by sliding a Rabin–Karp hash and putting the hashes in a
set: O(n) per test, O(n log n) overall. Mention that hashing gives false
positives and that you would verify a hit by direct comparison, or use double
hashing.

Suffix automaton or a suffix array with LCP gives a deterministic O(n) / O(n
log n), which is the right thing to *name* and the wrong thing to attempt in
40 minutes.
""",
        ),
    ],
}


def longest_repeating_substring(s: str) -> int:
    n = len(s)
    best = 0
    previous = [0] * (n + 1)  # row i - 1

    for i in range(1, n + 1):
        current = [0] * (n + 1)
        for j in range(i + 1, n + 1):  # strictly above the diagonal
            if s[i - 1] == s[j - 1]:
                current[j] = previous[j - 1] + 1  # extend the common suffix
                best = max(best, current[j])
            # else: leave 0 — a mismatch ends the run (substring, not subsequence)
        previous = current

    return best


CASES = [
    (("abcd",), 0),
    (("abbaba",), 2),
    (("aabcaabdaab",), 3),
    (("aaaa",), 3),
    (("abcabcabc",), 6),
    (("",), 0),
    (("a",), 0),
    (("aa",), 1),
]


def solve(s: str) -> int:
    return longest_repeating_substring(s)
