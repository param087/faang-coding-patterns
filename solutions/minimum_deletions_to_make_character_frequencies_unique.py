"""Minimum Deletions to Make Character Frequencies Unique — LeetCode 1647."""

from __future__ import annotations

from collections import Counter

META = {
    "pattern": "greedy",
    "insight": "Only the multiset of frequencies matters; walk them from largest down, dropping each clashing count to the first free slot below.",
    "time": "O(n + k log k) with k <= 26 distinct letters",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Delete the fewest characters from a lowercase string so that no two distinct
letters end up with the same non-zero frequency.

Note the phrasing carefully: a frequency of **zero** is allowed for any number
of letters, because a letter deleted entirely no longer has a frequency at all.
`"abcdef"` therefore costs 5, not 0 — five of the six letters must vanish.
""",
        ),
        (
            "The insight",
            """
The letters themselves are irrelevant. Count them, throw the identities away,
and you are left with a bag of numbers that must be made distinct using only
decrements, each decrement costing 1.

Process the counts in **descending** order, tracking which frequencies are
already taken. A count that clashes is decremented until it hits a free value
or reaches 0. Descending order is what makes this optimal: the largest counts
have the most room beneath them, and lowering a big count to make space for a
small one can never cost less than the reverse.

Concretely, carry a ceiling: clamp each count to `min(count, allowed)`, charge
`count - clamped` deletions, then lower the ceiling to `clamped - 1` (floored at
zero) for the next letter. Same "must sit strictly below the previous survivor"
shape as the interval-tightening problems.

The 26-letter bound is the reason `k log k` is effectively free — the real cost
is the O(n) counting pass, and it is worth saying so rather than quoting
O(n log n).
""",
        ),
        (
            "Edge cases",
            """
- **Frequencies may collapse to 0**, and multiple letters may sit at 0 — the
  clamp must floor at zero and stop consuming slots there. `"abcdef"` → 5 and
  `"aabbcc"` → 3 are the tests that catch a version which refuses to go below 1.
- **Already unique** (`"aab"`, `""`) → 0 deletions; the sweep must not fire.
- **Order matters, not the string.** Anagrams have identical answers; if your
  code depends on iteration order of the `Counter`, sort first.
- The naive fix — "for each clash, delete one character and recount" — is
  correct but O(n · 26) in the worst case for a problem that is one pass.
- The greedy is safe by an exchange argument: given any valid final assignment,
  re-matching the surviving frequencies to letters in descending order never
  increases the total deletions, so a descending sweep loses nothing.
""",
        ),
    ],
}


def min_deletions(s: str) -> int:
    deletions = 0
    allowed = len(s)  # no frequency can exceed the string length

    for count in sorted(Counter(s).values(), reverse=True):
        kept = min(count, allowed)
        deletions += count - kept
        allowed = max(kept - 1, 0)  # the next letter must sit strictly lower

    return deletions


CASES = [
    (("aab",), 0),
    (("aaabbbcc",), 2),
    (("ceabaacb",), 2),
    (("aaabbbccc",), 3),  # 3, 3, 3 -> 3, 2, 1
    (("abcdef",), 5),  # frequencies may fall all the way to zero
    (("aabbcc",), 3),
    (("a",), 0),
    (("",), 0),
]


def solve(s: str) -> int:
    return min_deletions(s)
