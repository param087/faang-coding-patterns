"""Prefix and Suffix Search — LeetCode 745."""

from __future__ import annotations

META = {
    "pattern": "tries",
    "symbol": "WordFilter",
    "insight": "Index every word under 'suffix#word' keys, and a two-sided query collapses into one ordinary prefix search for 'suffix#prefix'.",
    "time": "O(Σ L²) to build, O(|prefix| + |suffix|) per query",
    "space": "O(Σ L²) trie nodes",
    "sections": [
        (
            "What it asks",
            """
Preprocess a word list, then answer many queries of the form "largest index of a
word that starts with `prefix` **and** ends with `suffix`", or -1.

Two clarifications decide the design. **How many queries relative to words?**
Up to 10⁴ queries against 1.5·10⁴ words — so paying heavily at build time to
make queries O(query length) is the right trade. And **may prefix and suffix
overlap?** Yes: for the word `"a"`, the query `("a", "a")` matches. Any solution
that assumes the two parts occupy disjoint halves is wrong on short words.
""",
        ),
        (
            "The insight",
            """
A trie answers prefix questions. A trie over reversed words answers suffix
questions. Intersecting two such answers means storing an index *set* per node
and intersecting sets — at 1.5·10⁴ words that is the slow, fiddly answer.

Instead make the suffix part of the key. For each word `w` insert **every**
string

    w[i:] + "#" + w        for i = 0 … len(w)

and record the word's index at every node along the way, overwriting as index
increases so each node ends up holding the largest index that passes through it.

Then a query is a single descent on `suffix + "#" + prefix`. Matching that path
forces the stored key to begin with `suffix`, then the separator, then `prefix`
— and since every key is (a suffix of `w`) + `#` + `w` in full, that is exactly
"`w` ends with `suffix` and `w` starts with `prefix`". Include `i = len(w)` so
the empty suffix has a key, and `i = 0` so the whole word can serve as its own
suffix — that is the overlap case above.

Because the node value is written on the way down and later indices overwrite
earlier ones, the answer at the landing node is already the maximum. No search
below it, no set intersection.
""",
        ),
        (
            "The separator, and the cost you are agreeing to",
            """
`#` must be **outside the word alphabet**. With lowercase-only inputs it is; if
the alphabet is unrestricted, reuse of a real character silently merges keys —
`("ab", "")` would start matching words containing a literal `#`. State the
assumption or pick a sentinel you have checked, because this is a correctness
bug that no sample test exposes.

The build is `Σ over words of L·(2L + 1)` characters: at 1.5·10⁴ words of
length 10 that is ~3·10⁶ node steps, fine. At **L = 1000 it would be 2·10⁹** and
this approach is dead — then you fall back to a prefix trie plus a suffix trie
and intersect sorted index lists, or, if queries are few, just scan.

The hash-map variant — key every `prefix + "#" + suffix` pair directly into a
dict, `(L+1)² per word` — is simpler to write and O(1) per query, at a worse
build cost (121 keys per 10-character word rather than 10 insertions). Worth
naming as the "if you want it in five lines" alternative; the trie is the one
that generalises when the prefix set is not enumerable.
""",
        ),
    ],
}

SEPARATOR = "#"  # must not occur in any word


class _Node:
    __slots__ = ("best", "children")

    def __init__(self) -> None:
        self.children: dict[str, _Node] = {}
        self.best = -1  # largest word index whose key passes through here


class WordFilter:
    def __init__(self, words: list[str]) -> None:
        self.root = _Node()
        for index, word in enumerate(words):
            # i = 0 lets the whole word act as its own suffix; i = len(word)
            # gives the empty suffix a key.
            for i in range(len(word) + 1):
                node = self.root
                for char in word[i:] + SEPARATOR + word:
                    node = node.children.setdefault(char, _Node())
                    node.best = index  # ascending index, so this is the maximum

    def f(self, prefix: str, suffix: str) -> int:
        node = self.root
        for char in suffix + SEPARATOR + prefix:
            child = node.children.get(char)
            if child is None:
                return -1
            node = child
        return node.best


CASES = [
    ((["apple"], [("a", "e")]), [0]),
    (
        (["apple"], [("a", "e"), ("b", "e"), ("a", "f"), ("", ""), ("apple", "apple")]),
        [0, -1, -1, 0, 0],
    ),
    # Prefix and suffix overlap on a one-character word.
    ((["a"], [("a", "a"), ("a", ""), ("", "a")]), [0, 0, 0]),
    # Duplicates: the largest index wins, so the node value must be overwritten.
    ((["apple", "apple"], [("a", "e"), ("app", "le")]), [1, 1]),
    (
        (["bat", "bag", "bug"], [("b", "g"), ("ba", "g"), ("b", "t"), ("bu", ""), ("", "")]),
        [2, 1, 0, 2, 2],
    ),
    ((["ab"], [("abc", "b"), ("a", "abb")]), [-1, -1]),
    (([], [("a", "b")]), [-1]),
    ((["", "a"], [("", ""), ("a", "a")]), [1, 1]),
]


def solve(words: list[str], queries: list[tuple[str, str]]) -> list[int]:
    word_filter = WordFilter(words)  # fresh instance keeps solve pure
    return [word_filter.f(prefix, suffix) for prefix, suffix in queries]
