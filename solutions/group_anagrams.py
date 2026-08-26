"""Group Anagrams — LeetCode 49."""

from __future__ import annotations

from collections import defaultdict

META = {
    "pattern": "arrays-hashing",
    "insight": "Every anagram class needs one canonical name; make that name the dict key and the grouping falls out in a single pass.",
    "time": "O(n·k) with a count key, O(n·k log k) if you sort each word",
    "space": "O(n·k)",
    "sections": [
        (
            "What it asks",
            """
Given a list of strings, bucket them so that words which are rearrangements of
each other land together. **Any output order is accepted**, inside groups and
between them — confirm that, because it changes what you have to do.

Ask for the alphabet and the word length. Lowercase-only and `k ≤ 100` is the
signal that a 26-slot count key is available; arbitrary Unicode pushes you back
to sorting.
""",
        ),
        (
            "The insight",
            """
Comparing every pair is O(n²·k) and pointless. Instead, give each anagram class
a **canonical name** and let a hash map do the grouping:

```
"eat" -> "aet"      "tan" -> "ant"
"tea" -> "aet"      "nat" -> "ant"
"ate" -> "aet"      "bat" -> "abt"
```

One pass, one dict lookup per word. The whole problem reduces to choosing that
name well, which is the next section.

This is the shape to recognise: *whenever an equivalence relation has a cheap
canonical form, hashing that form turns a quadratic grouping into a linear
one.* The same move solves isomorphic strings, grouping shifted strings, and
grouping congruent islands.
""",
        ),
        (
            "Choosing the key",
            """
- **Sorted string** — `"".join(sorted(word))`. Simple, always correct, costs
  O(k log k) per word. Fine, and the one to write first.
- **26-slot count tuple** — `tuple(counts)`. O(k) per word, so the whole thing
  is O(n·k), and it is what the lowercase constraint is hinting at. Must be a
  `tuple`, not a `list`: lists are unhashable.

Two keys that look clever and are wrong:

- **A frozenset of characters** — throws away multiplicity, so `"aab"` and
  `"abb"` collide. That case is in the tests below for exactly this reason.
- **A product of primes** — one prime per letter, multiply. Cute, and in Python
  it even works because ints are arbitrary precision, but in Java or C++ it
  overflows on words of a few dozen characters and silently returns wrong
  groups. Mention it, then do not use it.
""",
        ),
    ],
}


def group_anagrams(strs: list[str]) -> list[list[str]]:
    groups: dict[tuple[int, ...], list[str]] = defaultdict(list)

    for word in strs:
        counts = [0] * 26
        for character in word:
            counts[ord(character) - ord("a")] += 1
        groups[tuple(counts)].append(word)  # tuple, because lists are unhashable

    return list(groups.values())


CASES = [
    (
        (["eat", "tea", "tan", "ate", "nat", "bat"],),
        [["ate", "eat", "tea"], ["bat"], ["nat", "tan"]],
    ),
    ((["aab", "abb"],), [["aab"], ["abb"]]),  # a frozenset-of-characters key merges these
    ((["aab", "aba", "baa", "ab", "ba", "b"],), [["aab", "aba", "baa"], ["ab", "ba"], ["b"]]),
    ((["ab", "ba", "abc", "cba", "bac"],), [["ab", "ba"], ["abc", "bac", "cba"]]),
    (([""],), [[""]]),
    ((["a"],), [["a"]]),
    (([],), []),
]


def solve(strs: list[str]) -> list[list[str]]:
    # LeetCode accepts any order; canonicalise so the cases stay deterministic.
    return sorted(sorted(group) for group in group_anagrams(strs))
