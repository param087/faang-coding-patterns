"""Palindromic Substrings — LeetCode 647."""

from __future__ import annotations

META = {
    "pattern": "string-algorithms",
    "insight": "Every palindrome nests shorter ones at the same centre, so Manacher counts them straight from the radii: (r + 1) // 2 per centre.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Count palindromic substrings of `s`, counting *occurrences*, not distinct
strings — `"aaa"` has 6, not 3. Confirm that, because the distinct-strings
variant is a completely different problem (Eertree or suffix automaton).
""",
        ),
        (
            "The insight",
            """
Expand-around-centre is the answer you should give first: 2n - 1 centres, each
expanded outward, O(n²) worst case. At n = 1000 that is 10⁶ comparisons — fine
for the stated constraints, and if you write it cleanly you have passed.

Manacher is the version worth knowing, and the counting step is what makes it
short. Interleave separators so every palindrome has an odd length:

```
s = "aba"  ->  t = "^#a#b#a#$"
```

Let `radius[i]` be how far the palindrome centred at `t[i]` extends. Every
palindrome of radius `r` contains one of radius `r - 2`, `r - 4`, … nested
inside it, so the number of *real* substrings centred at `i` is
`(radius[i] + 1) // 2`. Sum that over all centres and you are done — no second
pass, no set.

The linear time comes from the mirror. While `i` sits inside a known palindrome
ending at `right`, the radius at `i` is at least the radius at its mirror
`2·centre - i`, clipped to `right - i`. Only the part beyond `right` is ever
compared character by character, and `right` never moves backwards, so the
total comparison work is O(n).
""",
        ),
        (
            "Why the sentinels are not decoration",
            """
`^` and `$` at the ends are what let the expansion loop be a bare
`while t[i + r + 1] == t[i - r - 1]` with no bounds check. They never match
anything — not each other, not a `#`, not a letter — so every expansion stops
on its own.

Drop them and you get either an `IndexError` at the right edge or, worse in
Python, a silent wrap-around at the left edge where `t[-1]` is the last
character. That produces a plausible-looking wrong count rather than a crash,
which is the hardest kind of bug to spot in an interview.

The other trap is `min(right - i, radius[mirror])`. Without the clip you copy a
mirror radius that reaches outside the known palindrome, where nothing has been
verified. `"abaaba"` is the shortest input that exercises it.
""",
        ),
    ],
}


def count_substrings(s: str) -> int:
    if not s:
        return 0

    # Separators make every palindrome odd-length; sentinels stop the expansion.
    t = "^#" + "#".join(s) + "#$"
    radius = [0] * len(t)
    centre = right = 0
    total = 0

    for i in range(1, len(t) - 1):
        if i < right:
            radius[i] = min(right - i, radius[2 * centre - i])  # clip to what is known
        while t[i + radius[i] + 1] == t[i - radius[i] - 1]:
            radius[i] += 1
        if i + radius[i] > right:
            centre, right = i, i + radius[i]
        total += (radius[i] + 1) // 2  # nested palindromes at this centre

    return total


CASES = [
    (("abc",), 3),
    (("aaa",), 6),
    (("abba",), 6),
    (("aabaa",), 9),
    (("abacaba",), 12),
    (("aaaaa",), 15),
    (("a",), 1),
    (("",), 0),
]


def solve(s: str) -> int:
    return count_substrings(s)
