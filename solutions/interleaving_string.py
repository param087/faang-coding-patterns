"""Interleaving String — LeetCode 97."""

from __future__ import annotations

META = {
    "pattern": "dp-strings",
    "insight": "How much of each source you have consumed is the whole state — the position in s3 is their sum, so the table is 2-D, not 3-D.",
    "time": "O(m · n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Is `s3` formed by interleaving `s1` and `s2` — taking characters from the two
in any order while preserving each one's internal order?

The length check `len(s1) + len(s2) == len(s3)` is a hard precondition, not an
optimisation: without it a shorter `s3` can be "matched" by a prefix and you
return True.

Ask whether the interleaving must be strictly alternating (it must not — runs
from one source are fine) and whether either input can be empty (yes, and then
the answer is just an equality check).
""",
        ),
        (
            "The insight",
            """
The obvious state is `(i, j, k)`: how far into each of the three strings. But
`k = i + j` always — every character consumed from `s1` or `s2` produces
exactly one character of `s3`. Dropping `k` collapses a 3-D table to 2-D and
is the observation the problem is testing.

> `dp[i][j]` = can `s3[0 .. i+j-1]` be built from the first `i` of `s1` and
> the first `j` of `s2`?

The split is on where the **last** character of `s3` came from:

```
dp[i][j] = (dp[i-1][j] and s1[i-1] == s3[i+j-1])
        or (dp[i][j-1] and s2[j-1] == s3[i+j-1])
```

Base row and column are prefix-equality runs: `dp[0][j]` is True while `s2`'s
first `j` characters equal `s3`'s, and symmetrically for the column.

Rolled to one array, iterate `j` **forwards**: `dp[j]` still holds row `i-1`
(the "take from `s1`" term) while `dp[j-1]` has already been updated to row `i`
(the "take from `s2`" term). That is exactly what the recurrence wants — but
only if you also update `dp[0]` at the top of each row, which is the line that
gets dropped.
""",
        ),
        (
            "Why greedy fails",
            """
The tempting answer is a two-pointer scan: at each character of `s3`, take
from whichever of `s1`/`s2` matches. It breaks the moment **both** match and
the choice matters later.

`s1 = "aabcc"`, `s2 = "dbbca"`, `s3 = "aadbbcbcac"` → **True**, but a greedy
run that always prefers `s1` commits `s1`'s `c` at the wrong moment and dies.
Change the target one character to `"aadbbbaccc"` and the answer is **False**
— same prefixes, same first choices, opposite outcome. No local rule can tell
those two apart, which is the argument for the table, and it is worth stating
in exactly those terms before writing any code.

`("a", "a", "aa")` → True is the miniature version of the same trap and costs
nothing to keep as a test.

Follow-up worth pre-empting: the O(min(m, n)) space version is the rolled row
above with the shorter string chosen as the columns; and if they ask for the
actual interleaving, keep the full table and walk back from `(m, n)`.
""",
        ),
    ],
}


def is_interleave(s1: str, s2: str, s3: str) -> bool:
    m, n = len(s1), len(s2)
    if m + n != len(s3):  # precondition, not an optimisation
        return False

    dp = [False] * (n + 1)
    dp[0] = True
    for j in range(1, n + 1):  # base row: s2's prefix must equal s3's
        dp[j] = dp[j - 1] and s2[j - 1] == s3[j - 1]

    for i in range(1, m + 1):
        dp[0] = dp[0] and s1[i - 1] == s3[i - 1]  # base column, easy to forget
        for j in range(1, n + 1):
            from_s1 = dp[j] and s1[i - 1] == s3[i + j - 1]  # dp[j] is still row i-1
            from_s2 = dp[j - 1] and s2[j - 1] == s3[i + j - 1]  # already row i
            dp[j] = from_s1 or from_s2

    return dp[n]


CASES = [
    (("aabcc", "dbbca", "aadbbcbcac"), True),
    (("aabcc", "dbbca", "aadbbbaccc"), False),
    (("", "", ""), True),
    (("", "", "a"), False),
    (("a", "", "a"), True),
    (("", "b", "b"), True),
    (("a", "a", "aa"), True),
    (("abc", "def", "abcdef"), True),
]


def solve(s1: str, s2: str, s3: str) -> bool:
    return is_interleave(s1, s2, s3)
