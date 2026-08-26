"""Longest Palindrome — LeetCode 409."""

from __future__ import annotations

from collections import Counter

META = {
    "pattern": "arrays-hashing",
    "insight": "A palindrome pairs off every letter except at most one centre, so the answer is a parity count and nothing is ever built.",
    "time": "O(n)",
    "space": "O(1) — 52 letters at most",
    "sections": [
        (
            "What it asks",
            """
Given a string, return the **length** of the longest palindrome that can be
built by reordering some of its characters. Only the length; the arrangement
is never needed.

Ask: is it case sensitive? It is — `'A'` and `'a'` are different characters,
so `"Aa"` answers 1, not 2. That is the single most common wrong submission
here, and it is a clarifying question rather than a trick.
""",
        ),
        (
            "The insight",
            """
Read a palindrome from the outside in: every character has a mirror partner
except possibly one sitting exactly in the middle. So a multiset of characters
can be arranged into a palindrome of length

```
sum(count - count % 2 for every character) + (1 if any count is odd)
```

Position is irrelevant — you are free to reorder — which means no scanning for
substrings, no DP table, and no need to construct anything. Anyone who reaches
for the O(n²) expand-around-centre machinery from *Longest Palindromic
Substring* has answered a different question; this one is a frequency count.

The `+ 1` is capped at one because two odd-count characters cannot both take
the centre. `even_total < len(s)` is true exactly when at least one character
had an odd count, which saves a second pass over the counts.
""",
        ),
        (
            "Edge cases",
            """
- **Case sensitivity**: `"Aa"` → 1. Lowercasing the input is a wrong answer,
  not a simplification.
- Empty string → 0, and the `+ 1` must not fire: `even_total == len(s) == 0`,
  so the guard handles it without a special branch.
- All characters distinct (`"abc"`) → 1, because one of them can still be the
  centre.
- Every count even (`"bb"`, `"aabb"`) → the full length, `+ 1` suppressed.
- Odd counts above one still contribute: `"aaa"` gives 2 from the pair plus
  the centre, so 3. Discarding a whole letter because its count is odd is the
  other classic error.
- Follow-up worth pre-empting: *return the palindrome itself*. Emit
  `count // 2` copies of each character, the odd leftover in the middle, then
  the mirror image — O(n) and still one pass over the counts.
""",
        ),
    ],
}


def longest_palindrome(s: str) -> int:
    counts = Counter(s)

    # Every character contributes its largest even part as mirrored pairs.
    even_total = sum(count - count % 2 for count in counts.values())

    # A shortfall means some count was odd, so one character can take the centre.
    return even_total + 1 if even_total < len(s) else even_total


CASES = [
    (("abccccdd",), 7),
    (("Aa",), 1),  # case sensitive: 'A' and 'a' do not pair
    (("a",), 1),
    (("bb",), 2),
    (("aaa",), 3),  # odd counts above one still contribute their pairs
    (("aaabbbb",), 7),
    (("abc",), 1),
    (("",), 0),
]


def solve(s: str) -> int:
    return longest_palindrome(s)
