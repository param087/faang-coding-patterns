"""Design Add and Search Words Data Structure — LeetCode 211."""

from __future__ import annotations

META = {
    "pattern": "tries",
    "symbol": "WordDictionary",
    "insight": "A '.' turns the lookup from a walk into a search, so the trie must branch at that position — recursion, not a loop.",
    "time": "O(L) to add; O(L) to search with no dots, O(26^d · L) worst case with d dots",
    "space": "O(total characters added), O(L) recursion depth",
    "sections": [
        (
            "What it asks",
            """
Build a container supporting `add_word(word)` and `search(word)`, where the
searched word may contain `.` as a single-character wildcard. `search` returns
whether **some** added word matches.

Ask two things before writing anything:

- **Alphabet?** Lowercase a–z only, per the constraints. That bounds the
  fan-out at 26 and is what makes the wildcard cost sayable.
- **How many dots, and how many calls?** Up to 10⁴ calls, words up to 25 chars,
  and at most 3 dots per searched word. That last bound is the whole reason a
  branching search is acceptable — without it, `"..........."` against a dense
  trie is 26¹¹ paths.

A `set[str]` gives O(1) `add_word` and answers exact `search` too, so state
that first and then say why it collapses: with a wildcard you would have to
test every stored word, O(N · L) per query.
""",
        ),
        (
            "The insight",
            """
Without wildcards a trie search is a straight walk: consume a character, follow
that child, fail if it is missing. The `.` breaks the walk because there is no
single child to follow — **every** child is a candidate.

So the search becomes a DFS over the trie, parameterised by position in the
pattern:

- a concrete character narrows to at most one child (the cheap case);
- a `.` recurses into all present children.

The pruning is what makes this fast in practice. A `.` fans out into *the
children that exist*, not into 26 hypothetical ones — at depth 20 an English
word list has perhaps two or three live children per node, not 26. The 26^d
bound is real but it is a bound on a worst case that the constraints
(≤ 3 dots) keep out of reach.

Store children in a plain `dict[str, node]` and mark word ends with a boolean.
A fixed 26-slot list per node is faster to index but wastes memory on a sparse
trie, and — more importantly — makes the wildcard branch iterate 26 empty slots
instead of the two live ones.
""",
        ),
        (
            "Edge cases, and the one that fails",
            """
- **A pattern that is all dots.** `"..."` must match any stored word of length
  3 and nothing shorter or longer. The recursion handles length automatically
  because the base case is "pattern exhausted **and** this node is a word end"
  — dropping the `is_word` check makes `"..."` match a stored `"abcd"`, which
  is the single most common bug here.
- **A pattern longer than everything stored.** The walk runs out of children
  and returns `False`; no length pre-check is needed.
- **The empty string.** If `""` was never added, `search("")` is `False` —
  again from the `is_word` flag, not from a special case. LeetCode's
  constraints exclude it, but say it, because it proves the base case is right.
- **The same word added twice.** Idempotent; the flag is already set.
- **A stored word that is a prefix of another.** Adding `"bad"` then `"badge"`
  must leave `search("bad")` true. This is why word-ends are a flag on the node
  rather than "node has no children".
- **Deleting a word** (a natural follow-up): flip the flag off, then unwind and
  drop any node with no children and no flag. Reference-counting each node with
  a "words below here" integer is the version that stays O(L).
""",
        ),
    ],
}


class TrieNode:
    __slots__ = ("children", "is_word")

    def __init__(self) -> None:
        self.children: dict[str, TrieNode] = {}
        self.is_word = False


class WordDictionary:
    def __init__(self) -> None:
        self.root = TrieNode()

    def add_word(self, word: str) -> None:
        node = self.root
        for character in word:
            node = node.children.setdefault(character, TrieNode())
        node.is_word = True

    def search(self, word: str) -> bool:
        def dfs(index: int, node: TrieNode) -> bool:
            if index == len(word):
                return node.is_word  # not just "we got here"

            character = word[index]
            if character != ".":
                child = node.children.get(character)
                return child is not None and dfs(index + 1, child)

            # Wildcard: branch over the children that exist, not over 26 slots.
            return any(dfs(index + 1, child) for child in node.children.values())

        return dfs(0, self.root)


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    dictionary = WordDictionary()
    for word in ("bad", "dad", "mad"):
        dictionary.add_word(word)

    assert dictionary.search("pad") is False
    assert dictionary.search("bad") is True
    assert dictionary.search(".ad") is True
    assert dictionary.search("b..") is True

    # All dots: length must match exactly.
    assert dictionary.search("...") is True
    assert dictionary.search("..") is False
    assert dictionary.search("....") is False

    # A pattern longer than anything stored just runs out of children.
    assert dictionary.search("badly") is False

    # Prefix relationships: the word-end flag, not "is a leaf".
    nested = WordDictionary()
    nested.add_word("badge")
    assert nested.search("bad") is False
    nested.add_word("bad")
    assert nested.search("bad") is True
    assert nested.search("badge") is True
    assert nested.search("b...e") is True
    assert nested.search("b..g.") is True
    assert nested.search("b....") is True  # "badge" is 5 chars: b-a-d-g-e
    assert nested.search("b.....") is False  # six is one too many

    # Empty container, and the empty pattern.
    empty = WordDictionary()
    assert empty.search("") is False
    assert empty.search("a") is False
    assert empty.search(".") is False
    empty.add_word("")
    assert empty.search("") is True

    # Idempotent re-add.
    repeat = WordDictionary()
    repeat.add_word("mad")
    repeat.add_word("mad")
    assert repeat.search("mad") is True
    assert repeat.search("ma") is False

    # Wildcards in every position of a longer word.
    long_words = WordDictionary()
    long_words.add_word("interview")
    assert long_words.search(".........") is True
    assert long_words.search("interview") is True
    assert long_words.search("intervie.") is True
    assert long_words.search(".nterview") is True
    assert long_words.search("inte.view") is True
    assert long_words.search("inte.viex") is False
