"""Longest Palindromic Substring — LeetCode 5."""

from __future__ import annotations

META = {
    "pattern": "string-algorithms",
    "insight": "There are 2n-1 centres, not n — a palindrome can sit on a character or between two.",
    "time": "O(n²)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
The longest contiguous palindromic substring.

Ask: return the substring or its length; is any longest one acceptable when
there are ties (yes); is it case-sensitive; can the string be empty.
""",
        ),
        (
            "Brute force",
            """
Every substring checked for palindromicity: O(n³). At n = 1000 that is 10⁹.
""",
        ),
        (
            "The insight",
            """
A palindrome is defined by its **centre**. So rather than enumerating
substrings, enumerate centres and expand outward while the characters match.

O(n²) time and — worth saying — **O(1) space**, which beats the O(n²) DP
solution on memory. That is a real point in its favour, not a technicality.
""",
        ),
        (
            "2n − 1 centres, not n",
            """
This is the bug this problem has.

A palindrome can be centred **on a character** (odd length, `aba`) or
**between two characters** (even length, `abba`). So there are `2n − 1`
centres, and you must expand from both kinds.

Writing only the odd case passes `"babad"` and fails `"cbbd"`, returning
`"c"` instead of `"bb"`. Run `"cbbd"`.
""",
        ),
        (
            "Manacher",
            """
There is an O(n) algorithm. In one sentence: transform the string to
`^#c#b#b#d$` so every palindrome becomes odd-length, then reuse mirrored radii
the way the Z-function does.

**Say it exists, say it is O(n), and offer to write it only if invited.** It is
genuinely hard to get right under time pressure, and centre expansion is the
right answer in a 35-minute round.
""",
        ),
        (
            "Follow-ups",
            """
- **Palindromic Substrings** (count them all) — the identical expansion, but
  increment a counter on every successful expansion instead of tracking a
  maximum.
- **Longest Palindromic *Subsequence*** — a different problem. It is the LCS of
  the string with its own reverse, and it is
  [DP on strings](../../patterns/dp-strings/).
- **Shortest Palindrome** — prepend the fewest characters, solved with the KMP
  failure function over `s + "#" + reverse(s)`.
""",
        ),
    ],
}


def longest_palindrome(s: str) -> str:
    if not s:
        return ""

    start, length = 0, 1

    def expand(left: int, right: int) -> None:
        nonlocal start, length
        while left >= 0 and right < len(s) and s[left] == s[right]:
            left -= 1
            right += 1
        # The loop overshoots by one on each side.
        if right - left - 1 > length:
            start, length = left + 1, right - left - 1

    for i in range(len(s)):
        expand(i, i)  # odd length, centred on a character
        expand(i, i + 1)  # even length, centred between two

    return s[start : start + length]


CASES = [
    (("cbbd",), "bb"),  # even-length centre — the case that catches people
    (("a",), "a"),
    (("ac",), "a"),
    (("",), ""),
    (("aaaa",), "aaaa"),
    (("racecar",), "racecar"),
]


def solve(s: str) -> str:
    return longest_palindrome(s)


def check() -> None:
    for args, expected in CASES:
        assert longest_palindrome(*args) == expected

    # Ties are acceptable, so check membership rather than equality.
    assert longest_palindrome("babad") in {"bab", "aba"}
    assert longest_palindrome("abacdfgdcaba") in {"aba"}

    # Every result must actually be a palindrome and a real substring.
    for text in ("forgeeksskeegfor", "abcda", "xyzzyx", "ab"):
        result = longest_palindrome(text)
        assert result == result[::-1]
        assert result in text
