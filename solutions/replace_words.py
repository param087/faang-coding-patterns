"""Replace Words — LeetCode 648."""

from __future__ import annotations

META = {
    "pattern": "tries",
    "insight": "Walk each word down a trie of roots and stop at the first word-end: descending by length means the first hit is the shortest root.",
    "time": "O(D + S) — D total root characters, S total sentence characters",
    "space": "O(D) for the trie",
    "sections": [
        (
            "What it asks",
            """
Given a dictionary of roots and a sentence, replace every word that has a root
as a prefix by that root. If several roots match, use the **shortest**. Words
with no matching root are left alone; the sentence keeps its spacing as single
spaces.

Ask: lowercase only (yes), and can a root be longer than the word it is tested
against (yes — it simply does not match). The shortest-root rule is the part
worth repeating back, because it is what makes a single downward walk enough.
""",
        ),
        (
            "The insight",
            """
The naive shape is "for each word, for each root, does it prefix?" — with 1000
roots and 1000 words that is 10⁶ prefix comparisons, each up to 100 characters:
about 10⁸ character operations, and it re-walks the same shared prefixes over
and over.

A trie of the roots collapses all of them into one walk. For a word, descend
character by character; the moment you stand on a node marked as a root-end,
that root is the answer — and because you descend in increasing length, **the
first word-end you meet is necessarily the shortest matching root**. There is
no comparison of candidate lengths anywhere in the code; the traversal order
does it.

The walk stops for one of three reasons, and all three are one loop:

- you hit a word-end → emit that prefix;
- the next character has no child → no root matches, emit the word unchanged;
- the word runs out → same, emit unchanged.

A `set` of roots plus "try every prefix of the word, shortest first" is also
O(S) amortised and is a perfectly respectable answer for 1000 roots; the trie
wins when roots are long and heavily shared, and it is what the question is
fishing for. Say both.
""",
        ),
        (
            "Edge cases",
            """
- **Roots that prefix each other.** `["a", "aa", "aaa"]` against `"aaaa"` must
  give `"a"`. Any implementation that walks to the *deepest* word-end fails
  here — this is the discriminating case.
- **A root equal to the whole word.** `"cat"` with root `"cat"` → `"cat"`, and
  the loop hits the word-end on the final character rather than falling off the
  end. Both paths must emit the same string.
- **A root longer than the word.** `["catalogue"]` against `"cat"`: the word
  runs out before any word-end, so it is left alone. Off-by-one territory if
  you check word-ends only after consuming a character.
- **No roots at all**, or a word with no match: return the sentence unchanged.
- **Duplicate roots** in the dictionary are free — inserting twice is a no-op.
- **Punctuation or capitals** are out of scope by the constraints; if the
  interviewer adds them, normalise before the lookup and re-attach the original
  casing, because the trie must stay single-alphabet.
""",
        ),
    ],
}


class TrieNode:
    __slots__ = ("children", "is_root")

    def __init__(self) -> None:
        self.children: dict[str, TrieNode] = {}
        self.is_root = False


def replace_words(dictionary: list[str], sentence: str) -> str:
    root = TrieNode()
    for word in dictionary:
        node = root
        for character in word:
            node = node.children.setdefault(character, TrieNode())
        node.is_root = True

    def shortest_root(word: str) -> str:
        node = root
        for index, character in enumerate(word):
            child = node.children.get(character)
            if child is None:
                return word  # prefix went dead
            if child.is_root:
                return word[: index + 1]  # first word-end == shortest root
            node = child
        return word  # word ran out before any root ended

    return " ".join(shortest_root(word) for word in sentence.split())


CASES = [
    ((["cat", "bat", "rat"], "the cattle was rattled by the battery"), "the cat was rat by the bat"),
    ((["a", "b", "c"], "aadsfasf absbs bbab cadsfafs"), "a a b c"),
    # Nested roots: the shortest must win, not the deepest word-end reached.
    ((["a", "aa", "aaa", "aaaa"], "a aa aaa aaaa aaaaa"), "a a a a a"),
    # A root equal to the word, and a root longer than the word.
    ((["cat", "catalogue"], "cat catalogue catastrophe ca"), "cat cat cat ca"),
    ((["catalogue"], "cat"), "cat"),
    (([], "nothing changes here"), "nothing changes here"),
    ((["xyz"], ""), ""),
    ((["ab", "ab", "b"], "abc bcd cab"), "ab b cab"),  # duplicates are a no-op
]


def solve(dictionary: list[str], sentence: str) -> str:
    return replace_words(dictionary, sentence)
