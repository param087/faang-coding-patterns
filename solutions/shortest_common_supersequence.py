"""Shortest Common Supersequence — LeetCode 1092."""

from __future__ import annotations

META = {
    "pattern": "dp-strings",
    "insight": "Merge the two strings and let them share exactly the longest common subsequence — every other character has to be written out on its own.",
    "time": "O(m · n)",
    "space": "O(m · n) — the full table is needed to walk the answer back out",
    "sections": [
        (
            "What it asks",
            """
Return the shortest string that contains both `s1` and `s2` as subsequences.
The **string**, not its length, and any shortest one is accepted.

That last clause matters for testing: the answer is not unique, so a test that
compares against one fixed string is testing your tie-break rather than your
algorithm. The `check()` below verifies the two real properties instead —
both inputs are subsequences of the result, and the length is optimal.

Ask whether either string can be empty (yes; the answer is the other one).
""",
        ),
        (
            "The insight",
            """
Length first, because it makes the construction obvious:

```
len(SCS) = m + n - LCS(s1, s2)
```

Concatenating gives a supersequence of length `m + n`. Every character the two
strings **share along a common subsequence** can be written once instead of
twice, and the most you can share is the LCS. So build the LCS table, then walk
back from `(m, n)`:

- characters equal → emit it once, step diagonally (this is the sharing);
- otherwise step towards the larger of `dp[i-1][j]` and `dp[i][j-1]`, emitting
  the character you step past — it cannot be shared, so it must be written on
  its own.

When the walk hits an edge, the remaining prefix of whichever string is left
goes on the front verbatim. Exactly one of the two prefixes is non-empty, so
`s1[:i] + s2[:j]` is safe as a single expression.

The result comes out backwards, so reverse it — but reverse only the character
list, then prepend the prefix. Reversing after appending a multi-character
prefix scrambles that prefix, and it is a bug that survives every short test
case and fails on the first long one.
""",
        ),
        (
            "The tie-break, and the greedy answers that are wrong",
            """
On a mismatch, `dp[i-1][j] >= dp[i][j-1]` versus `>` picks a different valid
answer of the same length. Both are correct; do not let an interviewer's
sample output convince you that yours is broken — say "any shortest one is
accepted, here is why mine is shortest" and give the `m + n - LCS` argument.

Two wrong first answers:

- **Interleave greedily**, taking whichever character matches. Same failure as
  Interleaving String: when both sides could supply the next character the
  local choice does not determine the global optimum.
- **Share the longest common *substring*** instead of subsequence. On
  `s1 = "abac"`, `s2 = "cab"` the longest common substring is `"ab"` (length 2,
  as it happens the same as the LCS here), but on `s1 = "aaabbb"`,
  `s2 = "ababab"` the substring bound gives a much worse merge than the
  subsequence bound. Sharing does not require contiguity.

Space is the honest O(m · n): reconstruction reads the whole table, so the
rolled-row trick from the other problems in this pattern is unavailable. Say
so rather than claiming O(n) out of habit.
""",
        ),
    ],
}


def shortest_common_supersequence(s1: str, s2: str) -> str:
    m, n = len(s1), len(s2)

    dp = [[0] * (n + 1) for _ in range(m + 1)]  # dp[i][j] = LCS of the prefixes
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    merged: list[str] = []  # built back to front
    i, j = m, n
    while i > 0 and j > 0:
        if s1[i - 1] == s2[j - 1]:
            merged.append(s1[i - 1])  # shared, written once
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            merged.append(s1[i - 1])
            i -= 1
        else:
            merged.append(s2[j - 1])
            j -= 1

    # Reverse the characters first, then prepend — exactly one prefix is left.
    return s1[:i] + s2[:j] + "".join(reversed(merged))


def _is_subsequence(needle: str, haystack: str) -> bool:
    it = iter(haystack)
    return all(ch in it for ch in needle)


def _lcs_length(a: str, b: str) -> int:
    previous = [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        current = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                current[j] = previous[j - 1] + 1
            else:
                current[j] = max(previous[j], current[j - 1])
        previous = current
    return previous[len(b)]


CASES = [
    (("abac", "cab"), 5),
    (("aaaaaaaa", "aaaaaaaa"), 8),
    (("", "abc"), 3),
    (("abc", ""), 3),
    (("", ""), 0),
    (("abc", "def"), 6),
    (("aaabbb", "ababab"), 8),
    (("bbbaaaba", "bbababbb"), 11),
]


def solve(s1: str, s2: str) -> int:
    """The answer is not unique, so the comparable value is its length."""
    return len(shortest_common_supersequence(s1, s2))


def check() -> None:
    for (s1, s2), expected_length in CASES:
        result = shortest_common_supersequence(s1, s2)
        assert len(result) == expected_length, (s1, s2, result)
        assert solve(s1, s2) == expected_length, (s1, s2)
        # The two properties that actually define a correct answer.
        assert _is_subsequence(s1, result), (s1, result)
        assert _is_subsequence(s2, result), (s2, result)
        assert len(result) == len(s1) + len(s2) - _lcs_length(s1, s2), (s1, s2, result)
