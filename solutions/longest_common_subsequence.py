"""Longest Common Subsequence — LeetCode 1143."""

from __future__ import annotations

META = {
    "pattern": "dp-strings",
    "insight": "Two pointers, one into each string, are the whole state: either the last characters match and both advance, or one side is thrown away.",
    "time": "O(m · n)",
    "space": "O(min(m, n))",
    "sections": [
        (
            "What it asks",
            """
The length of the longest sequence of characters appearing in both strings in
the same relative order, not necessarily contiguously.

Ask two things. **Length or the actual string?** (Length here — reconstructing
it needs the full table, not the rolled row.) And **subsequence or
substring?** If the interviewer says substring, this recurrence is wrong; see
below.

This is the parent problem of the pattern. Edit Distance, Delete Operation,
Shortest Common Supersequence, Longest Palindromic Subsequence and Minimum
ASCII Delete Sum are all this table with a different scoring rule, so it is
worth being fluent enough to write it without thinking.
""",
        ),
        (
            "Brute force, and why it fails",
            """
Enumerate every subsequence of `a` and test each against `b`: 2^m subsets. At
m = n = 1000 — the actual LeetCode constraint — that is 2^1000, which is not a
number that fits in this universe.

The memoised version is the same recursion with the observation that only the
pair `(i, j)` matters, and there are just 1000 × 1000 = **10⁶** such pairs.
That gap, 2^1000 down to 10⁶, is the entire argument for the table.
""",
        ),
        (
            "The state",
            """
> `dp[i][j]` = the LCS length of the first `i` characters of `a` and the first
> `j` characters of `b`.

Two cases, and the split is on the **last** character of each prefix:

- `a[i-1] == b[j-1]` → that character can be in the LCS, and pairing it is
  never worse than not pairing it, so `dp[i][j] = dp[i-1][j-1] + 1`. No `max`
  is needed here; this is a real exchange argument, not hand-waving.
- otherwise the last characters cannot both be used, so drop one:
  `max(dp[i-1][j], dp[i][j-1])`.

Base row and column are 0 — nothing matches the empty string. That is the one
way this differs from Edit Distance, where row 0 is `0..n` because emptying a
string costs a deletion per character. Getting these two problems' base cases
crossed is the most common way to lose the interview from an otherwise correct
recurrence.
""",
        ),
        (
            "Subsequence vs substring — the recurrence that breaks",
            """
For the longest common **substring** (contiguous), the `else` branch is not
`max(...)`; it is **`0`**. `dp[i][j]` becomes the longest common *suffix* of
the two prefixes, and the answer is the running maximum over the table rather
than the bottom-right cell.

One character of difference, entirely different problem. If you cannot say
which one you are solving, you do not have the recurrence.
""",
        ),
        (
            "Rolling the table",
            """
Each row reads only from the row above and from cells to its left, so two rows
suffice: O(min(m, n)) after swapping so the shorter string indexes the row.

Say this, then say the caveat immediately: **reconstruction needs the full
table**, so if the follow-up asks for the string itself, the rolled version is
the wrong one to have written. Offer the rolled version as an optimisation you
would apply once the answer is agreed.
""",
        ),
        (
            "Dry run",
            """
`a = "abcde"`, `b = "ace"` → **3**.

Row for `a[0] = 'a'`: matches `b[0]`, so `dp[1] = [0, 1, 1, 1]`.

Row for `'b'`: no match anywhere, every cell inherits from above →
`[0, 1, 1, 1]`.

Row for `'c'`: `b[1] = 'c'` matches, `dp[3][2] = dp[2][1] + 1 = 2`, and the
2 propagates right → `[0, 1, 2, 2]`.

Row for `'d'`: no match, inherit → `[0, 1, 2, 2]`.

Row for `'e'`: matches `b[2]`, `dp[5][3] = dp[4][2] + 1 = 3`.

Now the counter-case: `a = "abc"`, `b = "def"` → **0**, and every cell in the
table is 0. Watching a whole table stay flat is a good sanity check that your
base cases are not silently seeding a 1.
""",
        ),
        (
            "Follow-ups",
            """
- **Return the string** — keep the full 2-D table and walk backwards from
  `(m, n)`: on a match, emit the character and step diagonally; otherwise step
  towards the larger of the two neighbours. O(m + n) to reconstruct.
- **Longest Palindromic Subsequence** — `LCS(s, reversed(s))`. Say this even
  if you then write the interval DP; recognising the reduction is the point.
- **Longest Increasing Subsequence of one array** — *not* this table. That is
  patience sorting in O(n log n). LCS of an array with its own sorted, deduped
  copy also works and is O(n²), which is a nice thing to know and usually the
  wrong thing to submit.
- **Beyond two strings** — LCS of `k` strings is NP-hard in `k`; the table
  becomes `n^k`. Worth knowing so you do not promise a generalisation you
  cannot deliver.
""",
        ),
    ],
}


def longest_common_subsequence(a: str, b: str) -> int:
    # Roll the shorter dimension so the extra space is O(min(m, n)).
    if len(b) > len(a):
        a, b = b, a

    cols = len(b)
    previous = [0] * (cols + 1)  # base row: nothing matches the empty string

    for i in range(1, len(a) + 1):
        current = [0] * (cols + 1)
        for j in range(1, cols + 1):
            if a[i - 1] == b[j - 1]:
                current[j] = previous[j - 1] + 1  # pairing is never worse
            else:
                current[j] = max(previous[j], current[j - 1])  # drop one side
        previous = current

    return previous[cols]


CASES = [
    (("abcde", "ace"), 3),
    (("abc", "abc"), 3),
    (("abc", "def"), 0),
    (("", "abc"), 0),
    (("", ""), 0),
    (("bsbininm", "jmjkbkjkv"), 1),
    (("oxcpqrsvwf", "shmtulqrypy"), 2),
    (("ezupkr", "ubmrapg"), 2),
]


def solve(a: str, b: str) -> int:
    return longest_common_subsequence(a, b)
