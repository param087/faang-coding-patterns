"""Longest Word in Dictionary — LeetCode 720."""

from __future__ import annotations

META = {
    "pattern": "tries",
    "insight": "A word is buildable only if every prefix is a word, so the answer is the deepest node reached stepping only through word-ends.",
    "time": "O(total characters)",
    "space": "O(total characters) for the trie",
    "sections": [
        (
            "What it asks",
            """
Return the longest word that can be built one character at a time, where every
intermediate string is also in the list. Ties go to the **lexicographically
smallest**; if nothing qualifies, return `""`.

The trap is reading "built one character at a time" as "some prefix is in the
list". It is *every* prefix: `"world"` needs `"w"`, `"wo"`, `"wor"`, `"worl"`
all present. Confirm that out loud — it changes the whole solution.

Ask whether the input is sorted (it is not) and whether duplicates can appear
(they can; harmless either way).
""",
        ),
        (
            "The insight",
            """
"Every prefix is also a word" is a statement about a trie: it says every node
on the path from the root is marked as a word-end. So the answer is the deepest
node you can reach **without ever stepping onto an unmarked node**, and the
search is a DFS that simply refuses to descend into a child that is not a word.

That refusal is the entire algorithm. There is no set membership test per
prefix, no re-scanning, no sorting of the input by length.

The tie-break falls out of the traversal order. Visit children in `a`..`z`
order and keep a candidate only when it is **strictly** longer than the current
best. At any given depth the alphabetically first reachable word is visited
first, so it is the one that gets recorded, and no later equal-length word can
displace it. Getting the tie-break for free is why the comparison is `>` and
not `>=` — flip it and you return the alphabetically *largest*.

The alternative — sort the words, then sweep with a `set`, keeping a word only
if `word[:-1]` is already accepted — is shorter to write and O(n log n · L).
Mention it; the trie is the version that generalises to a streaming dictionary.
""",
        ),
        (
            "Edge cases",
            """
- **Nothing buildable.** `["abc"]` has no `"a"`, so return `""`. The DFS never
  descends past the root and the initial best stays empty.
- **Single-character words are always buildable** — their only proper prefix is
  the empty string, which is free. This is the base of every valid chain, so a
  list with no length-1 word yields `""` no matter how long the entries are.
- **Ties.** `["a","banana","app","appl","ap","apply","apple"]` → both `"apple"`
  and `"apply"` are buildable at length 5; the answer is `"apple"`. Any solution
  that tracks "longest seen" without the alphabetical rule flips a coin here.
  Note `"banana"` is a decoy — `"b"` is missing, so its whole chain is dead.
- **Duplicates** in the input just re-set an already-set flag.
- **The empty string in the input** is excluded by the constraints; if allowed,
  it would be the root and would not change any answer.
""",
        ),
    ],
}


class TrieNode:
    __slots__ = ("children", "is_word")

    def __init__(self) -> None:
        self.children: dict[str, TrieNode] = {}
        self.is_word = False


def longest_word(words: list[str]) -> str:
    root = TrieNode()
    for word in words:
        node = root
        for character in word:
            node = node.children.setdefault(character, TrieNode())
        node.is_word = True

    best = ""

    def dfs(node: TrieNode, prefix: str) -> None:
        nonlocal best
        if len(prefix) > len(best):  # ">" not ">=": keeps the alphabetical first
            best = prefix
        for character in sorted(node.children):
            child = node.children[character]
            if child.is_word:  # refuse to step onto a gap in the chain
                dfs(child, prefix + character)

    dfs(root, "")
    return best


CASES = [
    ((["w", "wo", "wor", "worl", "world"],), "world"),
    ((["a", "banana", "app", "appl", "ap", "apply", "apple"],), "apple"),
    # No length-1 word, so no chain can start at all.
    ((["abc", "ab", "bc"],), ""),
    ((["a"],), "a"),
    # Tie at length 2 between two complete chains: alphabetical wins.
    ((["a", "b", "ab", "ba"],), "ab"),
    # "fgtvhd" is the longest entry but "fgtvh" is missing, so its chain is dead.
    ((["yo", "ew", "f", "fg", "fgt", "fgtv", "fgtvhd"],), "fgtv"),
    ((["a", "a", "aa", "aa", "aaa"],), "aaa"),  # duplicates
    (([],), ""),
]


def solve(words: list[str]) -> str:
    return longest_word(words)
