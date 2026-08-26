"""Rotate String — LeetCode 796."""

from __future__ import annotations

META = {
    "pattern": "string-algorithms",
    "insight": "Every rotation of s is a length-n window of s + s, so the whole question is one substring search in a doubled string.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Return whether `goal` can be reached from `s` by repeatedly moving the leading
character to the end — that is, whether `goal` is a rotation of `s`.

Ask whether rotations are only leftwards (yes on LeetCode, and it does not
matter: the set of left rotations equals the set of right rotations).
""",
        ),
        (
            "The insight",
            """
Concatenate `s` with itself. Reading `s + s` from offset `k` for `n`
characters gives exactly the rotation by `k`, for every `k` in `0..n-1`. So:

```
rotation  <=>  len(s) == len(goal)  and  goal is a substring of s + s
```

The length check is not optional — `"a"` is a substring of `"abab"` without
being a rotation of `"ab"`.

Two answers people give that are wrong: comparing sorted characters, and
comparing character counts. Both accept `("abab", "abba")`, which is an
anagram but not a rotation. Say the counter-example out loud; it is the fastest
way to show you actually checked.
""",
        ),
        (
            "Why not just write goal in s + s",
            """
You should write it — but know what you are leaning on. CPython's `in` is a
tuned two-way search that is linear in practice, so the one-liner is genuinely
O(n). In Java it is `indexOf`, which is the naive O(n·m) scan, and on
`s = "a"*n, goal = "a"*(n-1) + "b"` that is 2n² character comparisons —
2·10⁸ at n = 10⁴.

Under the string-algorithms banner the interviewer usually wants the search
spelled out, so the code below runs KMP over the doubled string: build the
prefix function of `goal`, stream `s + s` through it, never rewind. O(n) time,
O(n) space, no library behaviour to justify.

Edge case worth stating: two empty strings are rotations of each other, and the
KMP loop handles it only because the empty-needle case is returned early.
""",
        ),
    ],
}


def build_failure(pattern: str) -> list[int]:
    failure = [0] * len(pattern)
    k = 0

    for i in range(1, len(pattern)):
        while k and pattern[i] != pattern[k]:
            k = failure[k - 1]
        if pattern[i] == pattern[k]:
            k += 1
        failure[i] = k

    return failure


def contains(text: str, pattern: str) -> bool:
    if not pattern:
        return True

    failure = build_failure(pattern)
    k = 0

    for character in text:
        while k and character != pattern[k]:
            k = failure[k - 1]
        if character == pattern[k]:
            k += 1
        if k == len(pattern):
            return True

    return False


def rotate_string(s: str, goal: str) -> bool:
    if len(s) != len(goal):  # without this, "a" would "rotate" into "ab"
        return False
    return contains(s + s, goal)


CASES = [
    (("abcde", "cdeab"), True),
    (("abcde", "abced"), False),
    (("abab", "baba"), True),
    (("abab", "abba"), False),  # an anagram, not a rotation
    (("aaab", "aaba"), True),
    (("bbbacba", "bbbacba"), True),  # zero rotations counts
    (("a", "aa"), False),
    (("", ""), True),
]


def solve(s: str, goal: str) -> bool:
    return rotate_string(s, goal)
