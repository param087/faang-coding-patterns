"""Dynamic programming on strings and subsequences.

The state is almost always **two pointers, one into each string**: `dp[i][j]`
answers the question for the first i characters of `a` and the first j of `b`.
Once you accept that, the recurrence is a two-case split — the characters
match, or they do not.
"""

from __future__ import annotations


def longest_common_subsequence(a: str, b: str) -> int:
    """Length of the LCS.

    `dp[j]` is the previous row, rolled. `diagonal` holds `dp[i-1][j-1]`,
    which the update is about to destroy — saving it before overwriting is
    the whole trick to the one-dimensional version.
    """
    if not a or not b:
        return 0

    dp = [0] * (len(b) + 1)

    for i in range(1, len(a) + 1):
        diagonal = 0  # dp[i-1][j-1]
        for j in range(1, len(b) + 1):
            temp = dp[j]
            if a[i - 1] == b[j - 1]:
                dp[j] = diagonal + 1
            else:
                dp[j] = max(dp[j], dp[j - 1])
            diagonal = temp

    return dp[len(b)]


def edit_distance(a: str, b: str) -> int:
    """Minimum insert/delete/replace operations to turn a into b.

    Three predecessors, one per operation: delete from a (`dp[i-1][j]`),
    insert into a (`dp[i][j-1]`), replace (`dp[i-1][j-1]`). When the
    characters already match, the cost carries over from the diagonal for
    free.

    The base row and column are not zero — turning a string into the empty
    string costs one deletion per character.
    """
    rows, cols = len(a), len(b)
    previous = list(range(cols + 1))

    for i in range(1, rows + 1):
        current = [i] + [0] * cols
        for j in range(1, cols + 1):
            if a[i - 1] == b[j - 1]:
                current[j] = previous[j - 1]
            else:
                current[j] = 1 + min(
                    previous[j],  # delete
                    current[j - 1],  # insert
                    previous[j - 1],  # replace
                )
        previous = current

    return previous[cols]


def longest_palindromic_subsequence(s: str) -> int:
    """LPS length.

    The one-line reframing worth knowing: the longest palindromic subsequence
    of `s` is the LCS of `s` and `reversed(s)`. Recognising that saves you
    writing a second DP.
    """
    return longest_common_subsequence(s, s[::-1])


def is_match(s: str, pattern: str) -> bool:
    """Regular expression matching with `.` and `*`.

    `*` is what makes this hard, because it modifies the *preceding*
    character and can match zero occurrences. So the star case is a two-way
    branch: skip the pair entirely, or consume one character of `s` and stay
    on the same pattern position.

    The base row needs care: an empty string can still match `a*b*c*`, so
    `dp[0][j]` is true whenever the pattern so far is all star-pairs.
    """
    m, n = len(s), len(pattern)
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = True

    for j in range(1, n + 1):
        if pattern[j - 1] == "*" and j >= 2:
            dp[0][j] = dp[0][j - 2]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if pattern[j - 1] == "*" and j >= 2:
                # Zero occurrences of the preceding character...
                dp[i][j] = dp[i][j - 2]
                # ...or one more, if it matches.
                if pattern[j - 2] in {s[i - 1], "."}:
                    dp[i][j] = dp[i][j] or dp[i - 1][j]
            elif pattern[j - 1] in {s[i - 1], "."}:
                dp[i][j] = dp[i - 1][j - 1]

    return dp[m][n]


def num_distinct(s: str, t: str) -> int:
    """How many distinct subsequences of s equal t.

    Counting rather than optimising, so the recurrence *sums* instead of
    taking a max. When the characters match you may either use this
    occurrence or skip it — both are counted.
    """
    dp = [0] * (len(t) + 1)
    dp[0] = 1  # the empty target is matched exactly once, by the empty prefix

    for char in s:
        # Backwards, so each character of s is used at most once per position.
        for j in range(len(t), 0, -1):
            if t[j - 1] == char:
                dp[j] += dp[j - 1]

    return dp[len(t)]


CASES = [
    (("horse", "ros"), 3),
    (("intention", "execution"), 5),
    (("", "abc"), 3),
    (("abc", ""), 3),
    (("", ""), 0),
]


def solve(a: str, b: str) -> int:
    return edit_distance(a, b)


def check() -> None:
    for args, expected in CASES:
        assert edit_distance(*args) == expected

    assert longest_common_subsequence("abcde", "ace") == 3
    assert longest_common_subsequence("abc", "abc") == 3
    assert longest_common_subsequence("abc", "def") == 0
    assert longest_common_subsequence("", "a") == 0

    assert longest_palindromic_subsequence("bbbab") == 4
    assert longest_palindromic_subsequence("cbbd") == 2

    assert is_match("aa", "a") is False
    assert is_match("aa", "a*") is True
    assert is_match("ab", ".*") is True
    assert is_match("aab", "c*a*b") is True
    assert is_match("mississippi", "mis*is*p*.") is False
    assert is_match("", "a*") is True

    assert num_distinct("rabbbit", "rabbit") == 3
    assert num_distinct("babgbag", "bag") == 5
    assert num_distinct("abc", "") == 1
