"""Shortest Palindrome — LeetCode 214."""

from __future__ import annotations

SENTINEL = "\x00"  # any character guaranteed absent from the input

META = {
    "pattern": "string-algorithms",
    "insight": "Additions are front-only, so the answer hinges on the longest palindromic prefix — a border of s joined to its reverse.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
You may only add characters **in front of** `s`. Return the shortest string you
can reach that is a palindrome.

Two clarifications worth a sentence each. Additions are front-only — that
constraint is the entire problem, because it means the tail of `s` is fixed and
must be mirrored. And `s` can be up to 5·10⁴ characters, which rules out the
obvious quadratic.
""",
        ),
        (
            "Reframe it before you code",
            """
Whatever you prepend must mirror a suffix of `s`. So if `s = P + R` where `P`
is a palindrome, the answer is `reverse(R) + P + R` — and that is a palindrome
for **any** palindromic prefix `P`. Minimising the additions means maximising
`P`.

So the problem is: **find the longest prefix of `s` that is a palindrome.**
Everything after it gets reversed and stuck on the front.

Note the asymmetry that trips people up: it is the longest palindromic
*prefix*, not the longest palindromic *substring*. `"abbacd"` has palindromic
prefix `"abba"` and the answer is `"dc" + "abbacd"`; a longest-palindromic-
substring routine would happily hand back `"abba"` from the middle of a string
where it is useless.
""",
        ),
        (
            "Brute force, and why it fails",
            """
Walk `k` from `n` down to 1 and test whether `s[:k]` is a palindrome. Each test
is O(k), so the whole thing is O(n²). At n = 5·10⁴ that is 2.5·10⁹ character
comparisons, and it is not a pathological input — `"aaaa…a"` with one letter
changed at the end forces nearly every test to run to completion.

Manacher gets it to O(n) and is a legitimate answer: run it once, take the
largest palindrome whose left edge is index 0. But there is a shorter route.
""",
        ),
        (
            "The insight",
            """
A prefix of `s` is a palindrome exactly when it equals the corresponding suffix
of `reverse(s)`. That is the definition of a **border** — a prefix that is also
a suffix — of the joined string:

```
combined = s + SENTINEL + reverse(s)
```

The last entry of the KMP prefix function of `combined` is the length of its
longest border, and by construction that border is the longest palindromic
prefix of `s`. One linear pass, no palindrome test written anywhere.

```
longest = failure[-1]
answer  = reverse(s[longest:]) + s
```

The reason this reads as a trick is that the border is doing double duty:
matching forwards against `s` and backwards against `reverse(s)` at the same
time. Being able to state *why* the border is a palindrome — prefix of `s`
equals suffix of `reverse(s)` equals reverse of prefix of `s` — is what
separates recalling the trick from deriving it.
""",
        ),
        (
            "The separator is what makes it correct",
            """
Without `SENTINEL` the border can run past the midpoint and match across the
join, and you get a length greater than `len(s)`.

`s = "aaa"`. Then `combined = "aaaaaa"` and the longest border is `"aaaaa"`,
length 5 — larger than the string it is supposed to index into. Slicing with it
yields an empty tail and you return `"aaa"`, which happens to be right here,
and stops being right the moment the string is not uniform.

`s = "aaba"` is the one that bites. Without a separator
`combined = "aabaabaa"`, longest border `"aabaa"` = 5 > 4, so `s[5:]` is empty
and the function returns `"aaba"` — asserting that `"aaba"` is already a
palindrome. The correct answer is `"abaaba"`.

With the separator present, no border can contain it and none can span it, so
the reported length can never exceed `len(s)`. Pick any character outside the
input alphabet — a hash is fine for lowercase input, a NUL byte is fine for
anything. `min(failure[-1], len(s))` patches the symptom, not the cause.
""",
        ),
        (
            "Dry run",
            """
`s = "aacecaaa"`, `reverse(s) = "aaacecaa"`.

```
combined = a a c e c a a a | a a a c e c a a      (| is the separator)
```

The prefix function ends at 7: the border is `"aacecaa"`, which is indeed the
longest palindromic prefix. The tail `s[7:]` is `"a"`, so the answer is
`"a" + "aacecaaa"` = **`"aaacecaaa"`** — nine characters, one added.

Contrast `s = "abcd"`: the only palindromic prefix is `"a"`, so three
characters get prepended and the answer is `"dcbabcd"`.
""",
        ),
        (
            "Follow-ups",
            """
- **Append instead of prepend.** Same machinery mirrored: find the longest
  palindromic *suffix* by running the prefix function on
  `reverse(s) + SENTINEL + s`.
- **Why not a rolling hash?** It works — compare the forward and backward hash
  of each prefix in O(1) — and it is a fine second answer, but it is
  probabilistic and LeetCode has anti-hash tests for other problems in this
  family. KMP is deterministic and the same length of code.
- **Both ends allowed.** Then the answer is the whole longest-palindromic-
  substring problem plus a choice, and Manacher earns its place.
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


def shortest_palindrome(s: str) -> str:
    if not s:
        return ""

    # The separator stops a border from spanning the join; without it the
    # reported length can exceed len(s).
    combined = s + SENTINEL + s[::-1]
    longest = build_failure(combined)[-1]  # longest palindromic prefix of s

    return s[longest:][::-1] + s


CASES = [
    (("aacecaaa",), "aaacecaaa"),
    (("abcd",), "dcbabcd"),
    (("abbacd",), "dcabbacd"),
    (("aabba",), "abbaabba"),
    (("abab",), "babab"),
    (("aaa",), "aaa"),  # breaks the version with no separator
    (("aaba",), "abaaba"),
    (("a",), "a"),
    (("",), ""),
]


def solve(s: str) -> str:
    return shortest_palindrome(s)
