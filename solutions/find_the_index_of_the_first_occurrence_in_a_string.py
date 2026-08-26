"""Find the Index of the First Occurrence in a String — LeetCode 28."""

from __future__ import annotations

META = {
    "pattern": "string-algorithms",
    "insight": "A mismatch keeps most of the match: the prefix function says how much of the needle still lines up, so the text pointer never rewinds.",
    "time": "O(n + m)",
    "space": "O(m)",
    "sections": [
        (
            "What it asks",
            """
Return the index of the first occurrence of `needle` in `haystack`, or `-1`.

The clarifying question that changes the answer: **is the alphabet bounded,
and are we searching once or many times?** One search against one text is what
KMP is for. Many needles against one text is Aho-Corasick. One needle against
many texts is worth preprocessing the needle once and reusing the table — which
is exactly what the code below separates out.

`strStr("abc", "")` returns `0` by convention. Say so before you write it.
""",
        ),
        (
            "The insight",
            """
The naive scan restarts the needle from scratch on every mismatch, and rewinds
the text pointer with it. That is O(n·m) — at n = m = 10⁴ it is 10⁸ character
comparisons, and on `"aaaa...a"` versus `"aaaa...b"` it hits that worst case
exactly, which is the input an interviewer reaches for.

The information being thrown away is that **the characters already matched are
known**. If `needle[:k]` matched and `needle[k]` then failed, the next viable
alignment starts at the longest proper border of `needle[:k]` — the longest
prefix that is also a suffix. Precompute that for every `k` and the text
pointer only ever moves forward.

```
failure[i] = length of the longest proper border of needle[:i + 1]
```

Building the table is the same loop as the search, run against the needle
itself, which is why the two functions below look identical. Both are O(len)
amortised: `k` rises by at most 1 per step and every retreat lowers it, so the
inner `while` runs at most as many times in total as `k` was incremented.
""",
        ),
        (
            "Where the naive scan actually dies",
            """
The trap is the retreat line. `k = failure[k - 1]` is right; `k = 0` is the
version most people write from memory and it is wrong — it drops the shorter
borders that are still viable.

Needle `"aabaaac"` against text `"aabaaabaaac"`: after matching `"aabaaa"` the
`c` fails at `k = 6`. The correct retreat goes to `failure[5] = 2`, keeping the
trailing `"aa"` alive, and the match is then found at index 4. Reset-to-zero
skips straight past it and returns `-1` on longer variants of the same shape.

Borders chain — `failure[failure[k - 1] - 1]` and so on down to 0 — which is
why the retreat is a `while` and not an `if`.
""",
        ),
    ],
}


def build_failure(pattern: str) -> list[int]:
    """failure[i] = length of the longest proper prefix of pattern[:i+1] that is also a suffix."""
    failure = [0] * len(pattern)
    k = 0  # length of the border currently being extended

    for i in range(1, len(pattern)):
        while k and pattern[i] != pattern[k]:
            k = failure[k - 1]  # retreat to the next shorter border, not to 0
        if pattern[i] == pattern[k]:
            k += 1
        failure[i] = k

    return failure


def str_str(haystack: str, needle: str) -> int:
    if not needle:
        return 0  # stated convention, worth confirming out loud

    failure = build_failure(needle)
    k = 0  # how many characters of the needle currently match

    for i, character in enumerate(haystack):
        while k and character != needle[k]:
            k = failure[k - 1]
        if character == needle[k]:
            k += 1
        if k == len(needle):
            return i - k + 1

    return -1


CASES = [
    (("sadbutsad", "sad"), 0),
    (("leetcode", "leeto"), -1),
    (("mississippi", "issip"), 4),
    (("aabaaabaaac", "aabaaac"), 4),  # reset-to-zero returns -1 here
    (("aaaaa", "bba"), -1),
    (("aaa", "aaaa"), -1),  # needle longer than haystack
    (("abc", ""), 0),
    (("", ""), 0),
]


def solve(haystack: str, needle: str) -> int:
    return str_str(haystack, needle)
