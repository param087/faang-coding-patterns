"""Longest Common Prefix — LeetCode 14."""

from __future__ import annotations

META = {
    "pattern": "string-manipulation",
    "insight": "The answer can never be longer than the shortest word, so scan column by column and stop at the first mismatch.",
    "time": "O(S) where S is the total number of characters",
    "space": "O(1) beyond the returned slice",
    "sections": [
        (
            "What it asks",
            """
Return the longest string that starts every word in the list. Empty string if
there is no common start.

Ask two things: is the list ever **empty** (the signature has to answer it),
and is matching case-sensitive? Interviewers say "yes, empty is possible" and
"case-sensitive" — but the fact that you asked is the point.
""",
        ),
        (
            "The insight",
            """
The prefix only ever **shrinks**, and it is bounded by the shortest word. So
walk the columns of the shortest word and stop the moment any word disagrees:

```
flower
flow      <- runs out at column 4, so the answer is at most "flow"
flight
```

Column 0 `f`, column 1 `l`, column 2 `o` vs `i` → stop, return `"fl"`.

Cost is `O(S)` in the worst case (all words identical) but in practice it exits
after a couple of columns. The alternatives are all the same complexity dressed
differently:

- **Horizontal**: fold the prefix across the list, trimming as you go.
- **Sort and compare the ends**: after sorting, only the lexicographic **min**
  and **max** matter — everything between them shares their common prefix.
  A neat two-liner, but `O(n log n · m)`; mention it, do not lead with it.
- **Trie**: build one, walk down while there is exactly one child and no word
  terminates. Only worth it if you will answer many prefix queries.
""",
        ),
        (
            "Edge cases",
            """
- **Empty list** → `""`. Guard before you index `strs[0]`.
- **A word that is itself the prefix** (`["ab", "abc"]`). Iterating over the
  *shortest* word makes this fall out; iterating over `strs[0]` and indexing
  `word[i]` blindly throws `IndexError` on `["abc", "ab"]`.
- **An empty string in the list** → the answer is `""`, and the shortest-word
  loop handles it with no special case.
- **One word** → that word.
""",
        ),
    ],
}


def longest_common_prefix(strs: list[str]) -> str:
    if not strs:
        return ""

    shortest = min(strs, key=len)  # bounds the answer and kills the IndexError
    for i, char in enumerate(shortest):
        for other in strs:
            if other[i] != char:
                return shortest[:i]

    return shortest


CASES = [
    ((["flower", "flow", "flight"],), "fl"),
    ((["dog", "racecar", "car"],), ""),
    (([],), ""),
    ((["a"],), "a"),
    ((["abc", "ab"],), "ab"),
    ((["ab", "abc"],), "ab"),
    ((["abc", "abc", "abc"],), "abc"),
    ((["", "b"],), ""),
]


def solve(strs: list[str]) -> str:
    return longest_common_prefix(strs)
