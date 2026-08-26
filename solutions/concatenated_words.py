"""Concatenated Words — LeetCode 472."""

from __future__ import annotations

from functools import cache

META = {
    "pattern": "tries",
    "insight": "A word is concatenated iff some proper prefix of it is a dictionary word and the remaining suffix breaks into dictionary words at all.",
    "time": "O(n·k²) — one memoised word-break per word, each prefix walk O(k)",
    "space": "O(total characters) for the trie, O(k) memo per word",
    "sections": [
        (
            "What it asks",
            """
Given a list of distinct words, return those made **entirely of at least two
shorter words from the same list**. The pieces come from the list itself, which
is what makes it more than Word Break — the dictionary contains the very word
you are testing.

Ask whether the empty string can be in the list. Older versions of this problem
allowed it, and it makes every single word "concatenated" (`"" + "cat"`), which
is why solutions that pass locally fail on the hidden tests.
""",
        ),
        (
            "The insight",
            """
Insert every word into one trie, then run a word-break on each word against
that trie. The only difference from plain Word Break is a counting condition:
the split must use **two or more** pieces.

The clean way to enforce that — cleaner than threading a piece count through the
recursion, which fights memoisation because the answer then depends on the count
as well as the position — is to peel the first piece off by hand:

    concatenated(w) = any proper prefix w[:k] (0 < k < len(w)) is a word
                      and breakable(k)

where `breakable(i)` is the ordinary "does `w[i:]` split into one or more
dictionary words". `breakable` memoises on the index alone, and `breakable(0)`
— which would be trivially true, since `w` itself is in the trie — is never
called. That restriction to a *proper* prefix is the entire "at least two
pieces" rule, in one bound.

Sorting the words by length first is the other classic framing: insert only
words shorter than the current one, so the self-match cannot happen. It costs an
O(n log n) sort and an interleaved build; the proper-prefix bound gets there
without either, and lets you build the trie once up front.
""",
        ),
        (
            "Where the wrong answers come from",
            """
Three failure modes, all of which pass the sample:

- **`w` matching itself.** If you just ask "does `w` break into dictionary
  words?", every word answers yes. The proper-prefix bound `k < len(w)` is the
  guard; deleting `w` from the trie and reinserting it is the slow alternative.
- **Empty strings in the input.** Skip them at insert time *and* skip them as
  candidates. One empty word in the trie makes `breakable` true everywhere.
- **Counting pieces inside the memo.** `breakable(i, pieces)` has O(k²) states
  instead of O(k) and, worse, tempts you into caching a result that is only
  valid for one piece count. Keep the count out of the recursion entirely.

Complexity worth stating: n = 10⁴ words of up to k = 30 characters gives
`n·k² = 9·10⁶` character steps, which is why the O(k²) per word is fine here and
would not be at k = 10⁴.
""",
        ),
    ],
}


class _Node:
    __slots__ = ("children", "is_word")

    def __init__(self) -> None:
        self.children: dict[str, _Node] = {}
        self.is_word = False


def _is_concatenated(root: _Node, word: str) -> bool:
    length = len(word)

    @cache
    def breakable(start: int) -> bool:
        """Does word[start:] split into one or more dictionary words?"""
        if start == length:
            return True
        node = root
        for end in range(start, length):
            child = node.children.get(word[end])
            if child is None:
                return False  # nothing in the dictionary continues this path
            node = child
            if node.is_word and breakable(end + 1):
                return True
        return False

    node = root
    found = False
    for cut in range(length - 1):  # proper prefixes only: that is the "two or more"
        child = node.children.get(word[cut])
        if child is None:
            break
        node = child
        if node.is_word and breakable(cut + 1):
            found = True
            break

    breakable.cache_clear()
    return found


def find_all_concatenated_words_in_a_dict(words: list[str]) -> list[str]:
    root = _Node()
    for word in words:
        if not word:  # an empty word would make every other word "concatenated"
            continue
        node = root
        for char in word:
            node = node.children.setdefault(char, _Node())
        node.is_word = True

    return [word for word in words if word and _is_concatenated(root, word)]


CASES = [
    (
        (
            [
                "cat",
                "cats",
                "catsdogcats",
                "dog",
                "dogcatsdog",
                "hippopotamuses",
                "rat",
                "ratcatdogcat",
            ],
        ),
        ["catsdogcats", "dogcatsdog", "ratcatdogcat"],
    ),
    ((["cat", "dog", "catdog"],), ["catdog"]),
    # Nested: "catdogcat" is built from words that are themselves concatenated.
    ((["cat", "dog", "catdog", "dogcat", "catdogcat"],), ["catdog", "catdogcat", "dogcat"]),
    # Every word breaks into itself — only the proper-prefix bound keeps these out.
    ((["a", "abc", "hello"],), []),
    ((["a", "aa", "aaa"],), ["aa", "aaa"]),
    # An empty string in the input must not turn "a" into a concatenation.
    ((["", "a"],), []),
    ((["abc", "abcd"],), []),
    (([],), []),
]


def solve(words: list[str]) -> list[str]:
    return sorted(find_all_concatenated_words_in_a_dict(words))
