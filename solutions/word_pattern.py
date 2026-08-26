"""Word Pattern — LeetCode 290."""

from __future__ import annotations

META = {
    "pattern": "arrays-hashing",
    "insight": "Isomorphic Strings with words as the alphabet — plus a length check, because splitting can silently produce a different token count.",
    "time": "O(n) in the total length of s",
    "space": "O(w) — one entry per distinct word",
    "sections": [
        (
            "What it asks",
            """
Given a pattern of single letters and a sentence of space-separated words,
decide whether the sentence follows the pattern: a **bijection** between
letters and words that preserves order. `"abba"` and `"dog cat cat dog"`
follow; `"abba"` and `"dog dog dog dog"` do not, because `a` and `b` would
both map to `dog`.

Ask: can the sentence have leading, trailing or repeated spaces? That single
question decides between `s.split()` and `s.split(" ")`, and the two disagree
on `"dog  cat"`. LeetCode guarantees single spaces with no padding, so either
works there — but say which you assumed.
""",
        ),
        (
            "The insight",
            """
This is **Isomorphic Strings** with a different alphabet. Letter → word and
word → letter, both maintained, both checked. One direction alone accepts
`"abba" / "dog dog dog dog"`: `a -> dog`, `b -> dog`, no forward conflict, and
you return True on a case the problem statement explicitly rules out.

`setdefault` does insert-and-read in a single lookup, so each token costs one
hash per direction. The hashes are over whole words, which is what makes this
O(total characters) rather than O(len(pattern)) — worth saying if the
interviewer asks for the complexity in terms of the input size.
""",
        ),
        (
            "The length check is not defensive coding",
            """
It is the answer to a real test case. `zip` stops at the shorter sequence, so
without the guard `"aaa"` and `"aa aa aa aa"` walks three pairs, finds a
consistent bijection, and returns **True** — the wrong answer, because the
fourth word is never mapped to anything.

`strict=True` on `zip` would raise instead of silently truncating, but an
exception is not an answer; compare the lengths first and return False.

Related edge cases:

- Empty pattern with empty sentence → `[]` versus `""`, both length zero, so
  True. Empty pattern with a non-empty sentence → False via the same guard.
- A word may equal a pattern letter (`"a" / "a"`); the two maps are keyed
  separately, so there is no collision to worry about.
""",
        ),
    ],
}


def word_pattern(pattern: str, s: str) -> bool:
    words = s.split()
    if len(pattern) != len(words):
        return False  # zip would truncate and quietly accept

    char_to_word: dict[str, str] = {}
    word_to_char: dict[str, str] = {}

    for char, word in zip(pattern, words, strict=True):
        if char_to_word.setdefault(char, word) != word:
            return False
        if word_to_char.setdefault(word, char) != char:
            return False

    return True


CASES = [
    (("abba", "dog cat cat dog"), True),
    (("abba", "dog cat cat fish"), False),
    (("aaaa", "dog cat cat dog"), False),
    (("abba", "dog dog dog dog"), False),  # needs the word -> letter map
    (("aaa", "aa aa aa aa"), False),  # zip would truncate to three pairs
    (("abc", "b c a"), True),
    (("a", "dog"), True),
    (("", ""), True),
]


def solve(pattern: str, s: str) -> bool:
    return word_pattern(pattern, s)
