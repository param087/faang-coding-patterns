"""Implement Trie (Prefix Tree) — LeetCode 208."""

from __future__ import annotations

META = {
    "pattern": "tries",
    "symbol": "Trie",
    "insight": "One node per prefix, one flag marking a terminal word — the flag is what separates 'stored' from 'merely on the way'.",
    "time": "O(L) per operation, independent of dictionary size",
    "space": "O(total characters)",
    "sections": [
        (
            "What it asks",
            """
Implement `insert`, `search` (exact word) and `startsWith` (any word with this
prefix).

Ask: what is the alphabet; are insertions and searches interleaved; should
`search("app")` return true when only `"apple"` was inserted (**no** — that is
`startsWith`, and the distinction is the question).
""",
        ),
        (
            "The insight",
            """
A tree keyed by **position**: depth `d` branches on the `d`-th character. Words
sharing a prefix share a path.

The consequence is the reason to build one: **lookup costs O(L) in the length
of the query, and does not depend on how many words are stored.**
""",
        ),
        (
            "`is_word` is the whole problem",
            """
Without it, a trie cannot distinguish "apple is stored" from "app is merely on
the way to apple", and `search("app")` returns the wrong answer.

It is the first thing to write and the first thing people forget.
""",
        ),
        (
            "Why it beats a hash set",
            """
Say this — it is the "why does this data structure exist" question.

A set answers `search` in O(L) too. But it **cannot answer `startsWith`**
without scanning every key, because a hash destroys the prefix structure. The
trie shares prefixes, so the prefix query is free.
""",
        ),
        (
            "dict vs array children",
            """
A `dict` of children beats a fixed 26-slot array when the alphabet is large or
the branching sparse, and costs nothing when it is not.

Mention the array if the problem promises lowercase ASCII — it is faster in
practice. The dict is the safer default.
""",
        ),
        (
            "Follow-ups",
            """
- **`delete`** — harder than it looks. You must remove nodes only when they
  have no other children *and* are not themselves words, which means walking
  back up. Say that before attempting it.
- **Design Add and Search Words** — add `.` as a wildcard, which forces
  recursion and makes the worst case O(26^d) for `d` dots. Do not claim O(L).
- **Word Search II** — walk the grid once carrying a trie pointer instead of
  running one search per dictionary word.
""",
        ),
    ],
}


class Trie:
    def __init__(self) -> None:
        self.children: dict[str, Trie] = {}
        self.is_word = False  # distinguishes a stored word from a mere prefix

    def insert(self, word: str) -> None:
        node = self
        for char in word:
            node = node.children.setdefault(char, Trie())
        node.is_word = True

    def _walk(self, prefix: str) -> Trie | None:
        node = self
        for char in prefix:
            child = node.children.get(char)
            if child is None:
                return None
            node = child
        return node

    def search(self, word: str) -> bool:
        node = self._walk(word)
        return node is not None and node.is_word

    def starts_with(self, prefix: str) -> bool:
        return self._walk(prefix) is not None


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    trie = Trie()
    trie.insert("apple")
    assert trie.search("apple") is True
    assert trie.search("app") is False  # a prefix is not a stored word
    assert trie.starts_with("app") is True
    trie.insert("app")
    assert trie.search("app") is True  # now it is

    assert trie.starts_with("apx") is False
    assert trie.search("appl") is False
    assert trie.search("applesauce") is False

    empty = Trie()
    assert empty.search("") is False
    assert empty.starts_with("") is True  # every trie has the empty prefix
    empty.insert("")
    assert empty.search("") is True
