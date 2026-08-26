"""Longest Palindromic Subsequence — LeetCode 516."""

from __future__ import annotations

META = {
    "pattern": "dp-strings",
    "insight": "A palindromic subsequence of s is a common subsequence of s and its reverse — or, directly, an interval DP grown outwards from the diagonal.",
    "time": "O(n²)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
The length of the longest subsequence of `s` that reads the same forwards and
backwards. Characters need not be contiguous.

Ask whether they want the length or the string, and confirm **subsequence, not
substring** — Longest Palindromic Substring is a different problem with a
different algorithm (expand around centres, or Manacher).
""",
        ),
        (
            "The insight",
            """
Two routes, and you should name both.

**The reduction:** `LPS(s) = LCS(s, reversed(s))`. Any common subsequence of
`s` and its reverse reads the same either way. This is a one-line answer if
you already have LCS written, and stating it shows you see the pattern rather
than a problem.

**The interval DP**, which is what is written below and what generalises:

> `dp[i][j]` = the longest palindromic subsequence inside `s[i..j]`.

- `s[i] == s[j]` → those two characters wrap the best answer strictly inside:
  `dp[i+1][j-1] + 2`.
- otherwise one of them cannot be used: `max(dp[i+1][j], dp[i][j-1])`.
- `dp[i][i] = 1`, and `dp[i][j] = 0` when `i > j`.

Prefer the interval version if a follow-up is coming, because "count the
palindromic subsequences" and "minimum insertions to make a palindrome" are
the same table and the LCS reduction does not carry to them cleanly.
""",
        ),
        (
            "Iteration order — where this goes wrong",
            """
`dp[i][j]` depends on row `i+1`. A naive `for i in range(n)` reads cells that
have not been computed yet and silently returns garbage, usually a number
slightly too small, which passes `"bbbab"` and fails on longer inputs.

**`i` must run downwards** (`n-1 → 0`) and `j` upwards from `i+1`. Equivalently,
loop over increasing interval length. Every interval DP has this constraint;
say out loud which order you are using before you write the loops.

The rolled 1-D version below keeps the previous row (`i + 1`) only, so
`previous[j-1]` is `dp[i+1][j-1]` — the diagonal — and `current[j-1]` is
`dp[i][j-1]`. Mixing those two up is the same bug in a smaller space budget.

Two edges worth stating: `""` → 0, and the answer is at least 1 for any
non-empty string, since a single character is a palindrome.
""",
        ),
    ],
}


def longest_palindrome_subseq(s: str) -> int:
    n = len(s)
    if n == 0:
        return 0

    previous = [0] * n  # row i + 1

    for i in range(n - 1, -1, -1):  # must descend: dp[i] reads dp[i + 1]
        current = [0] * n
        current[i] = 1  # a single character is a palindrome
        for j in range(i + 1, n):
            if s[i] == s[j]:
                current[j] = previous[j - 1] + 2  # dp[i + 1][j - 1]
            else:
                current[j] = max(previous[j], current[j - 1])
        previous = current

    return previous[n - 1]


CASES = [
    (("bbbab",), 4),
    (("cbbd",), 2),
    (("",), 0),
    (("a",), 1),
    (("ab",), 1),
    (("aaaa",), 4),
    (("agbdba",), 5),
    (("abcdefg",), 1),
]


def solve(s: str) -> int:
    return longest_palindrome_subseq(s)
