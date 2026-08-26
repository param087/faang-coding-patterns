"""Index Pairs of a String — LeetCode 1065."""

from __future__ import annotations

META = {
    "pattern": "tries",
    "insight": "Anchor at each start index and walk the trie forward through the text: one pass finds every word starting there, already sorted.",
    "time": "O(D + n·L) — D total dictionary characters, L the longest word",
    "space": "O(D) for the trie, plus the output",
    "sections": [
        (
            "What it asks",
            """
This one is **premium**, so the statement is not public — described here in my
own words.

Given a string `text` and a list of `words`, return every pair `[i, j]` such
that `text[i..j]` (inclusive) is one of the words. Pairs come back sorted by
`i` first, then by `j`.

Matches **overlap freely** — this is not tokenisation and not a greedy
left-to-right scan. `"ababa"` with `["aba"]` yields both `[0,2]` and `[2,4]`,
sharing the middle `a`. Confirm that, and confirm whether a duplicated entry in
`words` should produce a duplicated pair (it should not; a trie makes the
question vanish).
""",
        ),
        (
            "The insight",
            """
The naive version is one substring test per (word, position) pair:
`text.find(word)` in a loop, or `text[i:i+len(w)] == w` for every `i` and every
`w`. With `n = 100` and 20 words that is nothing — but the shape is bad, and
the interviewer is asking because the shape is bad: it re-compares shared
prefixes once per word.

Anchor instead. Fix a start index `i` and walk **forward through the text**
while descending the trie of words. Every word-end node you pass gives one
answer `[i, j]`, and you keep going, because a longer word may also start at
`i` (`"an"` and `"anagram"` both do). The walk stops when the next character
has no child — one failed dict lookup ends every word sharing that dead prefix
at once.

The sorted output is free and that is the elegant part. The outer loop runs `i`
ascending, and the inner walk emits `j` ascending, so pairs come out already in
the required order. Any solution that collects then sorts is doing work the
traversal already did.

An Aho–Corasick automaton drops the `L` factor to a single O(n) pass by adding
suffix links, and is the right answer if `text` is a megabyte. Name it; do not
write it unless asked.
""",
        ),
        (
            "Edge cases",
            """
- **Overlapping matches.** `"ababa"` / `["aba"]` → `[[0,2],[2,4]]`. A scanner
  that jumps `i` past a match returns only the first and is the classic wrong
  answer here.
- **Nested matches at the same start.** `"anagram"` / `["a","an","anagram"]` →
  `[0,0]`, `[0,1]`, `[0,6]` all fire from the same anchor, which is why the
  walk must not stop at the first word-end.
- **A word longer than the remaining text.** The walk runs off the end of
  `text`; guard the index, or iterate `range(i, len(text))` so it cannot.
- **Duplicates in `words`** collapse into the same terminal node, so the output
  has no duplicate pairs without any extra check.
- **No matches at all** → `[]`, not `[[]]`.
- **The empty string as a word** would mark the root as terminal and produce a
  degenerate zero-length "match"; the constraints exclude it, but say so, since
  the loop as written never inspects the root and so silently ignores it.
""",
        ),
    ],
}


class TrieNode:
    __slots__ = ("children", "is_word")

    def __init__(self) -> None:
        self.children: dict[str, TrieNode] = {}
        self.is_word = False


def index_pairs(text: str, words: list[str]) -> list[list[int]]:
    root = TrieNode()
    for word in words:
        node = root
        for character in word:
            node = node.children.setdefault(character, TrieNode())
        node.is_word = True

    pairs: list[list[int]] = []
    for start in range(len(text)):
        node = root
        for end in range(start, len(text)):
            node = node.children.get(text[end])
            if node is None:
                break  # this prefix is dead for every word at once
            if node.is_word:
                pairs.append([start, end])  # keep walking: longer words may follow
    return pairs  # already sorted by start, then end


CASES = [
    (("thestoryofleetcodeandme", ["story", "fleet", "leetcode"]), [[3, 7], [9, 13], [10, 17]]),
    # Overlapping matches: the second starts inside the first.
    (("ababa", ["aba", "ab"]), [[0, 1], [0, 2], [2, 3], [2, 4]]),
    # Three words ending at different lengths from the same anchor.
    (
        ("anagram", ["a", "an", "anagram", "gram"]),
        [[0, 0], [0, 1], [0, 6], [2, 2], [3, 6], [5, 5]],
    ),
    # A word longer than the text it is tested against.
    (("cat", ["catalogue", "cat", "at"]), [[0, 2], [1, 2]]),
    (("abc", ["xyz"]), []),
    (("aaaa", ["a", "a", "aa"]), [[0, 0], [0, 1], [1, 1], [1, 2], [2, 2], [2, 3], [3, 3]]),
    (("", ["a"]), []),
    (("abc", []), []),
]


def solve(text: str, words: list[str]) -> list[list[int]]:
    return index_pairs(text, words)
