"""Stream of Characters — LeetCode 1032."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "tries",
    "symbol": "StreamChecker",
    "insight": "Every match must end on the character just received, so store the words reversed and walk the stream backwards.",
    "time": "O(L) per query, where L is the longest word; O(total characters) to build",
    "space": "O(total characters) for the trie, O(L) for the buffer",
    "sections": [
        (
            "What it asks",
            """
Build a checker over a fixed dictionary. Characters arrive one at a time, and
after each one you must say whether **any suffix of the stream so far** spells
a dictionary word.

Ask two things before writing anything: is the dictionary fixed at construction
(yes — that is what buys you the preprocessing), and how long is the stream? It
is unbounded, so anything that keeps the whole stream is wrong on memory even
when it is right on answers.
""",
        ),
        (
            "The insight",
            """
The naive move is a forward trie plus a set of "live" trie pointers that you
advance on every character. That works, but the live set can grow to O(L)
pointers and the bookkeeping is fiddly to get right under time pressure.

Turn it around. A match must **end** at the newest character. So walk
*backwards* from the newest character, and store the dictionary **reversed**.
Now one pointer, one loop:

- push the letter onto a buffer;
- from the newest character backwards, descend the reversed trie;
- the moment a node is marked `is_word`, some suffix of the stream is a word;
- the moment a character is missing from `children`, no longer suffix can match
  either — every longer candidate has this one as its own suffix. Stop.

That early exit is what makes the per-query cost O(L) rather than O(stream).
""",
        ),
        (
            "Bounding the buffer, and when to reach for Aho-Corasick",
            """
Keep the buffer at `maxlen = L`, the longest dictionary word. Anything older
cannot participate in a match, and a plain list that grows forever is the bug
that ships: correct answers, then memory death at 4·10⁴ queries.

`deque(maxlen=L)` gives you the cap for free — but note you must still iterate
it with `reversed(...)`, not slice it, since a deque has no O(1) slicing.

The honest complexity statement: **O(L) per query, not O(1)**. With `L ≤ 200`
and 4·10⁴ queries that is 8·10⁶ character steps, comfortably fast. If the
interviewer pushes for worst-case O(1) amortised, the answer is
**Aho-Corasick** — the same reversed trie plus suffix links, so a failed match
falls back to the longest proper suffix that is still alive instead of
restarting the descent. Name it; building it is rarely what they want in
45 minutes.
""",
        ),
    ],
}


class _Node:
    __slots__ = ("children", "is_word")

    def __init__(self) -> None:
        self.children: dict[str, _Node] = {}
        self.is_word = False


class StreamChecker:
    def __init__(self, words: list[str]) -> None:
        self.root = _Node()
        longest = 0
        for word in words:
            if not word:
                continue
            longest = max(longest, len(word))
            node = self.root
            for char in reversed(word):  # reversed: matches are found back-to-front
                node = node.children.setdefault(char, _Node())
            node.is_word = True
        # Nothing older than the longest word can ever take part in a match.
        self.stream: deque[str] = deque(maxlen=longest or 1)

    def query(self, letter: str) -> bool:
        self.stream.append(letter)
        node = self.root
        for char in reversed(self.stream):
            child = node.children.get(char)
            if child is None:
                return False  # no longer suffix can match either
            if child.is_word:
                return True
            node = child
        return False


CASES = [
    ((["cd", "f", "kl"], "abcdefghijkl"), [False] * 3 + [True, False, True] + [False] * 5 + [True]),
    # A shorter word sits on the path of a longer one: must test is_word at every depth.
    ((["ab", "b"], "ab"), [False, True]),
    # Overlapping matches ending one character apart.
    ((["ab", "ba"], "aba"), [False, True, True]),
    ((["a", "aa"], "aaa"), [True, True, True]),
    # The match only completes at the very end of the stream.
    ((["abcd"], "xabcd"), [False, False, False, False, True]),
    ((["xyz"], "abc"), [False, False, False]),
    ((["abcde"], "abc"), [False, False, False]),
    (([], "ab"), [False, False]),
]


def solve(words: list[str], letters: str) -> list[bool]:
    checker = StreamChecker(words)  # fresh instance keeps solve pure
    return [checker.query(letter) for letter in letters]
