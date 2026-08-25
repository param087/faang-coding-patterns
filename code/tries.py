"""Tries — prefix trees, and the bitwise variant.

A trie is a tree keyed by position: depth d branches on the d-th character.
That makes prefix queries O(L) regardless of how many words are stored, which
is the whole reason to build one.

The bitwise version keys on bits instead of characters and is how max-XOR
problems become O(32n).
"""

from __future__ import annotations


class Trie:
    """Insert, exact search, and prefix search.

    A plain dict of children beats a fixed 26-slot array when the alphabet is
    large or sparse, and it costs nothing when it is not. `is_word` is what
    distinguishes "apple is stored" from "app is merely a prefix".
    """

    def __init__(self) -> None:
        self.children: dict[str, Trie] = {}
        self.is_word = False

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


class WildcardTrie(Trie):
    """Adds `.` matching any single character.

    The wildcard is what forces recursion: at a `.` you must try every child,
    so the search branches. Worst case O(26^d) for d dots, which is worth
    stating rather than claiming O(L).
    """

    def search(self, word: str) -> bool:
        def dfs(node: Trie, i: int) -> bool:
            if i == len(word):
                return node.is_word
            char = word[i]
            if char == ".":
                return any(dfs(child, i + 1) for child in node.children.values())
            child = node.children.get(char)
            return child is not None and dfs(child, i + 1)

        return dfs(self, 0)


class BitTrie:
    """Binary trie over fixed-width integers, for maximum-XOR queries.

    Insert every number as a path of bits, most significant first. To maximise
    the XOR with a query, greedily walk toward the *opposite* bit at each
    level — a differing high bit is worth more than every lower bit combined,
    which is why greedy is optimal here.
    """

    def __init__(self, width: int = 32) -> None:
        self.width = width
        self.root: dict[int, dict] = {}

    def insert(self, value: int) -> None:
        node = self.root
        for shift in range(self.width - 1, -1, -1):
            bit = (value >> shift) & 1
            node = node.setdefault(bit, {})

    def max_xor(self, value: int) -> int:
        if not self.root:
            return 0
        node = self.root
        best = 0
        for shift in range(self.width - 1, -1, -1):
            bit = (value >> shift) & 1
            want = 1 - bit
            if want in node:
                best |= 1 << shift
                node = node[want]
            else:
                node = node[bit]
        return best


def find_maximum_xor(nums: list[int]) -> int:
    """Largest XOR of any two values in the list. O(32n)."""
    trie = BitTrie()
    best = 0
    for value in nums:
        trie.insert(value)
        best = max(best, trie.max_xor(value))
    return best


CASES = [
    (([3, 10, 5, 25, 2, 8],), 28),
    (([0],), 0),
    (([2, 4],), 6),
    (([14, 70, 53, 83, 49, 91, 36, 80, 92, 51, 66, 70],), 127),
]


def solve(nums: list[int]) -> int:
    return find_maximum_xor(nums)


def check() -> None:
    for args, expected in CASES:
        assert find_maximum_xor(*args) == expected

    trie = Trie()
    trie.insert("apple")
    assert trie.search("apple") is True
    assert trie.search("app") is False  # a prefix is not a stored word
    assert trie.starts_with("app") is True
    assert trie.starts_with("apx") is False

    wildcard = WildcardTrie()
    for word in ("bad", "dad", "mad"):
        wildcard.insert(word)
    assert wildcard.search("pad") is False
    assert wildcard.search("bad") is True
    assert wildcard.search(".ad") is True
    assert wildcard.search("b..") is True
    assert wildcard.search("b....") is False
