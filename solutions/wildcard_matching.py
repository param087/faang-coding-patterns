"""Wildcard Matching — LeetCode 44."""

from __future__ import annotations

META = {
    "pattern": "dp-strings",
    "insight": "A free-standing star has two moves — swallow one more character of s, or stop — so the cell is just dp[i-1][j] or dp[i][j-1].",
    "time": "O(m · n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Match `s` against a pattern where `?` is any single character and `*` is any
sequence of characters, **including the empty one**. The whole string must be
covered.

Ask whether `*` can match the empty sequence — it can, and `("", "*")` → True
and `("", "***")` → True are the cases that check it. Ask whether the pattern
may contain other regex metacharacters: it may not, everything else is a
literal.
""",
        ),
        (
            "The insight",
            """
> `dp[i][j]` = does the first `i` characters of `s` match the first `j` of `p`?

Three cases, and the star one is the only interesting cell:

- `p[j-1] == '*'` → `dp[i][j-1]` (the star stops here, matching nothing more)
  **or** `dp[i-1][j]` (the star swallows `s[i-1]` and stays open). No `and`,
  no atom, no `j - 2`.
- `p[j-1]` is `?` or equals `s[i-1]` → `dp[i-1][j-1]`.
- otherwise `False`.

Base row: `dp[0][j]` is True only while the pattern is *all* stars, so
`dp[0][j] = dp[0][j-1] and p[j-1] == '*'`. That single line handles `"***"`
and every leading-star prefix, and it is the piece people forget — leaving it
False breaks `("adceb", "*a*b")` because the leading `*` never gets permission
to match nothing.

O(m · n) time, one rolled row for O(n) space.
""",
        ),
        (
            "How it differs from Regular Expression Matching",
            """
These two get merged in people's heads and the merge is fatal. The difference
is that `*` here is a **token**, and in problem 10 it is a **modifier on the
token before it**.

| | 44 wildcard | 10 regex |
|---|---|---|
| `*` alone | legal, matches anything | illegal, needs an atom |
| star cell | `dp[i][j-1] or dp[i-1][j]` | `dp[i][j-2] or (atom matches and dp[i-1][j])` |
| `a*` means | `a` then anything | zero or more `a` |
| base row | all-stars prefix | `dp[0][j] = dp[0][j-2]` |
| greedy solution | **yes**, O(1) space | **no** |

That last row is the follow-up worth having ready. Because a wildcard star can
absorb *any* characters, you can scan greedily: remember the position of the
most recent `*` and the point in `s` you were at when you used it; on a
mismatch, rewind to that `*`, let it eat one more character, and carry on.
O(m + n) time and O(1) space. Regex `*` cannot do this, because its star is
restricted to one atom and rewinding does not cover the branching.

`("acdcb", "a*c?b")` → **False** is the case that punishes a greedy attempt
written without the rewind: the `*` looks satisfied early and then `?b` runs
out of room.
""",
        ),
    ],
}


def is_match(s: str, p: str) -> bool:
    m, n = len(s), len(p)

    previous = [False] * (n + 1)  # row 0: s is empty
    previous[0] = True
    for j in range(1, n + 1):
        previous[j] = previous[j - 1] and p[j - 1] == "*"  # only an all-star prefix

    for i in range(1, m + 1):
        current = [False] * (n + 1)  # current[0]: non-empty s, empty p
        for j in range(1, n + 1):
            if p[j - 1] == "*":
                current[j] = current[j - 1] or previous[j]  # stop, or swallow one
            elif p[j - 1] in ("?", s[i - 1]):
                current[j] = previous[j - 1]
        previous = current

    return previous[n]


CASES = [
    (("aa", "a"), False),
    (("aa", "*"), True),
    (("cb", "?a"), False),
    (("adceb", "*a*b"), True),
    (("acdcb", "a*c?b"), False),
    (("", "***"), True),
    (("", ""), True),
    (("abc", ""), False),
    (("abcabczzzde", "*abc???de*"), True),
]


def solve(s: str, p: str) -> bool:
    return is_match(s, p)
