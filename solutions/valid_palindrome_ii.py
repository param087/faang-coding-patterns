"""Valid Palindrome II — LeetCode 680."""

from __future__ import annotations

META = {
    "pattern": "two-pointers",
    "insight": "At the first mismatch there are exactly two repairs — drop the left character or the right one — and each is a plain palindrome check.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Can `s` be made a palindrome by deleting **at most one** character? Return a
boolean, not the resulting string.

"At most" includes zero: an already-palindromic string is a yes. Ask whether
the input is guaranteed lowercase letters (on this problem it is — no case
folding or punctuation stripping, unlike Valid Palindrome I).
""",
        ),
        (
            "The insight",
            """
Walk the standard two pointers inwards. Everything matched before the first
mismatch is settled: those pairs are correct and neither of them is the
character you would delete, because deleting a matched character just shifts
the problem without fixing anything.

At the first mismatch `s[left] != s[right]`, your one deletion **must** be one
of those two characters — no other deletion changes that pair. So there are
exactly two candidates, and each leaves a substring that must be a palindrome
outright, with no budget left. Two linear checks on top of one linear scan:
`O(n)` total, `O(1)` space.

The recursion never goes deeper than one level. That is the whole trick, and
it is why this is `O(n)` rather than the `O(n²)` you would get by re-running
the outer scan after each trial deletion.
""",
        ),
        (
            "You must try both sides",
            """
The common wrong answer tries one side only — usually "skip the left
character" — and it fails on `"cbbcc"`. The outer `c`s match; then `b` vs `c`
mismatches. Skipping the left leaves `"bc"`, not a palindrome. Skipping the
right leaves `"bb"`, which is. Answer: **true**, and a one-sided solution says
false. `"ccbbc"` is the mirror case that breaks a right-only solution.

Both branches failing is a genuine false — `"cupuu"` fails both ways.

Follow-ups:

- **"At most k deletions?"** The two-branch trick does not generalise; the
  branching becomes `O(2^k · n)`. The expected answer is
  `n - LPS(s) <= k`, where `LPS` is the longest palindromic subsequence
  — an `O(n²)` DP. Say the bound, not just the DP.
- **"Return the palindrome, not a boolean?"** Trivial once you know which
  branch succeeded — but you have to record it, so restructure the helper to
  return the index it dropped.
""",
        ),
    ],
}


def _is_palindrome(s: str, left: int, right: int) -> bool:
    while left < right:
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    return True


def valid_palindrome(s: str) -> bool:
    left, right = 0, len(s) - 1

    while left < right:
        if s[left] != s[right]:
            # Exactly two repairs, and neither gets a second deletion.
            return _is_palindrome(s, left + 1, right) or _is_palindrome(s, left, right - 1)
        left += 1
        right -= 1

    return True  # already a palindrome; "at most one" allows zero


CASES = [
    (("aba",), True),
    (("abca",), True),
    (("cbbcc",), True),  # only dropping the RIGHT character works
    (("ccbbc",), True),  # mirror: only dropping the LEFT character works
    (("cupuu",), False),  # both branches fail — a genuine no
    (("abc",), False),
    (("a",), True),
    (("",), True),
]


def solve(s: str) -> bool:
    return valid_palindrome(s)
