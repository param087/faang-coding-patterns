"""Linear-time string machinery: KMP, Z-function, rolling hash, Manacher.

Rare, but nothing else saves you when they appear — and the failure function
in particular shows up disguised, as "shortest repeated unit" or "shortest
palindrome you can build by prepending".
"""

from __future__ import annotations


def build_failure(pattern: str) -> list[int]:
    """KMP failure function: `f[i]` = longest proper prefix of pattern[:i+1]
    that is also a suffix of it.

    This table *is* KMP. Once you have it, matching never backtracks in the
    text: on a mismatch you slide the pattern forward by what you already
    matched instead of restarting.
    """
    failure = [0] * len(pattern)
    length = 0

    for i in range(1, len(pattern)):
        while length > 0 and pattern[i] != pattern[length]:
            length = failure[length - 1]  # fall back, don't restart
        if pattern[i] == pattern[length]:
            length += 1
        failure[i] = length

    return failure


def kmp_search(text: str, pattern: str) -> int:
    """Index of the first occurrence of pattern in text, or -1. O(n + m)."""
    if not pattern:
        return 0

    failure = build_failure(pattern)
    matched = 0

    for i, char in enumerate(text):
        while matched > 0 and char != pattern[matched]:
            matched = failure[matched - 1]
        if char == pattern[matched]:
            matched += 1
        if matched == len(pattern):
            return i - len(pattern) + 1

    return -1


def z_function(s: str) -> list[int]:
    """`z[i]` = length of the longest common prefix of s and s[i:].

    Often easier to reason about than KMP, and it answers "does the pattern
    occur here" for every position at once when you run it over
    `pattern + sentinel + text`.
    """
    n = len(s)
    z = [0] * n
    left = right = 0

    for i in range(1, n):
        if i < right:
            z[i] = min(right - i, z[i - left])  # reuse the known window
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] > right:
            left, right = i, i + z[i]

    if n:
        z[0] = n
    return z


def rabin_karp(text: str, pattern: str, base: int = 256, mod: int = 1_000_000_007) -> int:
    """First occurrence via a rolling hash. O(n + m) expected.

    The reason to know it: it generalises to "find any duplicated substring of
    length L", which binary-searches over L and is the standard answer to
    Longest Duplicate Substring. Always verify a hash hit with a real string
    comparison — collisions are rare, not impossible.
    """
    n, m = len(text), len(pattern)
    if m == 0:
        return 0
    if m > n:
        return -1

    high = pow(base, m - 1, mod)
    target = 0
    rolling = 0
    for i in range(m):
        target = (target * base + ord(pattern[i])) % mod
        rolling = (rolling * base + ord(text[i])) % mod

    for i in range(n - m + 1):
        if rolling == target and text[i : i + m] == pattern:
            return i
        if i + m < n:
            rolling = ((rolling - ord(text[i]) * high) * base + ord(text[i + m])) % mod

    return -1


def longest_palindrome(s: str) -> str:
    """Longest palindromic substring by expanding around each centre. O(n²).

    Manacher gets this to O(n) but is hard to write correctly under pressure.
    Centre expansion is the right answer in a round: 2n - 1 centres, because
    a palindrome can be centred on a character or between two.
    """
    if not s:
        return ""

    start, length = 0, 1

    def expand(left: int, right: int) -> None:
        nonlocal start, length
        while left >= 0 and right < len(s) and s[left] == s[right]:
            left -= 1
            right += 1
        if right - left - 1 > length:
            start, length = left + 1, right - left - 1

    for i in range(len(s)):
        expand(i, i)  # odd length
        expand(i, i + 1)  # even length

    return s[start : start + length]


CASES = [
    (("sadbutsad", "sad"), 0),
    (("leetcode", "leeto"), -1),
    (("hello", "ll"), 2),
    (("aaa", "aaaa"), -1),
    (("abc", ""), 0),
]


def solve(text: str, pattern: str) -> int:
    return kmp_search(text, pattern)


def check() -> None:
    for args, expected in CASES:
        assert kmp_search(*args) == expected
        assert rabin_karp(*args) == expected

    assert build_failure("aabaaac") == [0, 1, 0, 1, 2, 2, 0]
    assert build_failure("abcabc") == [0, 0, 0, 1, 2, 3]

    assert z_function("aaaaa") == [5, 4, 3, 2, 1]
    assert z_function("aabxaab") == [7, 1, 0, 0, 3, 1, 0]
    assert z_function("") == []

    assert longest_palindrome("babad") in {"bab", "aba"}
    assert longest_palindrome("cbbd") == "bb"
    assert longest_palindrome("a") == "a"
    assert longest_palindrome("") == ""
