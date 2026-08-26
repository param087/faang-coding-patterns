"""Delete Operation for Two Strings — LeetCode 583."""

from __future__ import annotations

META = {
    "pattern": "dp-strings",
    "insight": "Whatever survives the deletions is a common subsequence, so the cheapest plan keeps the longest one: m + n − 2·LCS.",
    "time": "O(m · n)",
    "space": "O(min(m, n))",
    "sections": [
        (
            "What it asks",
            """
Only one operation is allowed — delete a character from either string — and
you need the fewest deletions that make the two strings equal.

Ask what "equal" means at the end (the same string, not the empty string; the
empty string is always reachable in `m + n` deletions and is the trivial upper
bound). Ask whether deletions from the two strings are counted together: they
are, which is why the answer is a single number.
""",
        ),
        (
            "The insight",
            """
Deleting never reorders and never inserts. So the common string you end up
with is a **subsequence of both inputs** — and conversely any common
subsequence is reachable by deleting everything else. The cheapest plan
therefore keeps the *longest* common subsequence:

```
answer = m + n - 2 * LCS(a, b)
```

The factor of 2 is the part people drop: each character not in the LCS must be
deleted from *its own* string, and there are `m - LCS` of them on one side and
`n - LCS` on the other.

You can also write it as a direct DP where `dp[i][j]` is the deletion cost of
the two prefixes, with `dp[i][0] = i`, `dp[0][j] = j`, and the mismatch branch
`1 + min(dp[i-1][j], dp[i][j-1])`. It is the same table; the reduction is
faster to write and much easier to defend. Note the missing third term: unlike
Edit Distance there is no **replace**, so `dp[i-1][j-1] + 1` is not an option
and a replace-shaped answer will come out one too small on `("a", "b")`.
""",
        ),
        (
            "Edge cases and the neighbours",
            """
- Either string empty → the answer is the other's length; the DP handles this
  through the zero base row of LCS.
- Both empty → 0. Identical strings → 0, since the LCS is the whole string.
- `("a", "b")` → **2**, not 1. This is the case that catches anyone who
  reused Edit Distance without removing the replace term.
- Disjoint alphabets → `m + n`, everything goes.

**Minimum ASCII Delete Sum** (LeetCode 712) is the same problem weighted by
character code, and it is *not* solved by maximising the LCS — the longest
common subsequence and the most valuable one are different strings. Run the
DP on sums directly. Being able to say why the reduction fails there is worth
more than the solution here.
""",
        ),
    ],
}


def min_distance(a: str, b: str) -> int:
    # Roll the shorter dimension so the extra space is O(min(m, n)).
    short, long = (a, b) if len(a) <= len(b) else (b, a)

    cols = len(short)
    previous = [0] * (cols + 1)

    for i in range(1, len(long) + 1):
        current = [0] * (cols + 1)
        for j in range(1, cols + 1):
            if long[i - 1] == short[j - 1]:
                current[j] = previous[j - 1] + 1
            else:
                current[j] = max(previous[j], current[j - 1])
        previous = current

    lcs = previous[cols]
    return len(a) + len(b) - 2 * lcs  # each unmatched character goes


CASES = [
    (("sea", "eat"), 2),
    (("leetcode", "etco"), 4),
    (("", "abc"), 3),
    (("abc", ""), 3),
    (("", ""), 0),
    (("abc", "abc"), 0),
    (("ab", "ba"), 2),
    (("a", "b"), 2),
]


def solve(a: str, b: str) -> int:
    return min_distance(a, b)
