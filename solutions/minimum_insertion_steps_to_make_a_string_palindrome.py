"""Minimum Insertion Steps to Make a String Palindrome — LeetCode 1312."""

from __future__ import annotations

META = {
    "pattern": "dp-strings",
    "insight": "Every character you never have to touch is part of a palindromic subsequence, so the answer is n minus the longest one.",
    "time": "O(n²)",
    "space": "O(n) — two rolling rows",
    "sections": [
        (
            "What it asks",
            """
Insertions are allowed **anywhere**, any character. Return the fewest needed to
make `s` a palindrome.

Ask: insertions only, or also deletions and replacements? (Only insertions —
which is what makes the answer a clean subsequence question. The delete-only
and insert-or-delete variants have the *same* numeric answer here, and saying
so is a good signal.) Case-sensitive, and can `s` be empty?
""",
        ),
        (
            "The insight",
            """
Flip the question. Insertions never remove anything, so the original string
survives inside the final palindrome. Ask which characters you *keep untouched*
— they must already read the same forwards and backwards, i.e. they form a
**palindromic subsequence** of `s`. Every other character needs a mirror
inserted for it, one insertion each.

So the answer is `n - LPS(s)`, and

> `LPS(s) = LCS(s, reversed(s))`

which drops you straight into the standard two-pointer-into-two-strings table.
The recurrence is plain LCS:

```
if a[i-1] == b[j-1]:  dp[i][j] = dp[i-1][j-1] + 1
else:                 dp[i][j] = max(dp[i-1][j], dp[i][j-1])
```

Only the previous row is ever read, so one rolling row gives O(n) space.

The direct interval DP is equally valid and the same cost — `dp[i][j]` = cost
for `s[i..j]`, carrying the diagonal when `s[i] == s[j]` and otherwise
`1 + min(dp[i+1][j], dp[i][j-1])`. Reach for it if you cannot justify the
reversal trick under pressure; reach for LCS if you want O(n) space.
""",
        ),
        (
            "Why LCS-with-its-own-reverse is legitimate",
            """
This is the step an interviewer will push on, and "it's a known trick" is not
an answer. The claim is `LCS(s, reverse(s)) = LPS(s)`.

- **≥**: any palindromic subsequence of `s` is also a subsequence of
  `reverse(s)` (read it backwards — it is the same string), so it is a common
  subsequence. Hence `LCS ≥ LPS`.
- **≤**: take any common subsequence `t` of `s` and `reverse(s)`. Then
  `reverse(t)` is a subsequence of `reverse(s)` reversed, which is `s`. The
  subtlety is that `t` itself need not be a palindrome — `LCS("ab", "ba")` can
  be `"a"` or `"b"`. What *is* true is that some longest common subsequence can
  always be chosen palindromic, by taking the two index sequences and folding
  them together from the outside in. That is the part worth stating out loud
  rather than waving at.

The wrong first answer people give is "count the characters with odd frequency"
— that solves the *anagram* version (**Longest Palindrome**, LC 409) where you
may reorder freely. Here order is fixed, so `"mbadm"` needs 2 insertions even
though its letters could be rearranged into a palindrome with 0.
""",
        ),
    ],
}


def min_insertions(s: str) -> int:
    n = len(s)
    if n < 2:
        return 0

    reverse = s[::-1]
    previous = [0] * (n + 1)  # LCS row for the empty prefix

    for i in range(1, n + 1):
        current = [0] * (n + 1)
        for j in range(1, n + 1):
            if s[i - 1] == reverse[j - 1]:
                current[j] = previous[j - 1] + 1  # extend the match
            else:
                current[j] = max(previous[j], current[j - 1])
        previous = current

    longest_palindromic_subsequence = previous[n]
    return n - longest_palindromic_subsequence  # one insertion per unmatched char


CASES = [
    (("zzazz",), 0),
    (("mbadm",), 2),
    (("leetcode",), 5),
    (("abcda",), 2),
    (("aacabdkacaa",), 2),
    (("abcabc",), 3),
    (("ab",), 1),
    (("",), 0),
]


def solve(s: str) -> int:
    return min_insertions(s)
