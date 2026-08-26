"""Design Search Autocomplete System — LeetCode 642."""

from __future__ import annotations

from heapq import nsmallest

META = {
    "pattern": "tries",
    "symbol": "AutocompleteSystem",
    "insight": "Hang the candidate set on every node of the path and keep a cursor, so a keystroke is one pointer hop plus a top-3 of that node.",
    "time": "O(k) per keystroke where k is the candidates under the prefix; O(L) to commit a sentence",
    "space": "O(total sentence characters × sentences sharing them)",
    "sections": [
        (
            "What it asks",
            """
This one is **premium**, so the statement is not public — described here in my
own words.

Build a search box backed by a history of sentences with visit counts:

- `AutocompleteSystem(sentences, times)` — seed the history.
- `input(c)` — the user typed `c`. If `c` is `'#'`, the sentence typed so far
  is committed to the history (count + 1), the buffer resets, and the call
  returns an empty list. Otherwise append `c` to the buffer and return the
  **top three** historical sentences having the buffer as a prefix, ranked by
  count descending, ties broken by **ASCII order ascending**.

Sentences contain lowercase letters and spaces, and the space sorts before
every letter (32 < 97) — which is exactly the tie-break that a naive
"alphabetical" mental model gets wrong.

Ask what the query mix is. This is a production autocomplete: reads outnumber
writes by orders of magnitude, so paying more on commit to make each keystroke
cheap is the right trade, and saying that is half the answer.
""",
        ),
        (
            "The insight",
            """
Two moving parts, and they are usually confused with each other:

1. **Finding the candidates.** A trie whose node for prefix `p` carries the
   counts of *every* sentence passing through it — `dict[sentence, count]`.
   Then "which sentences start with `p`?" is a read of one node, not a subtree
   walk. This costs memory (a sentence of length L appears in L maps) but the
   alternative — DFS the subtree on every keystroke — is O(subtree) per
   character, and the subtree under `"i"` in a real corpus is enormous.
2. **Ranking them.** `heapq.nsmallest(3, items, key=lambda kv: (-kv[1], kv[0]))`
   is O(k) for fixed 3, versus O(k log k) for a full sort. The key is the whole
   ranking rule in one tuple: negate the count so higher counts sort first,
   then the sentence itself ascending for the tie.

The third part is the one people miss: **keep a cursor**. Store the current
trie node between calls and advance it by one child per keystroke. Re-walking
the buffer from the root on every character makes typing an n-character query
O(n²) — for a 100-character query that is 5 000 hops instead of 100, and it is
the difference between a design that scales and one that merely works.
""",
        ),
        (
            "The dead prefix, and other things that break it",
            """
- **Once the prefix leaves the trie, it must stay gone.** Type `"i a"` where no
  history entry starts that way: the walk falls off at `'a'`. Every subsequent
  character must also return `[]` *without* consulting the trie — a cursor
  reset to the root, or a lookup that silently starts over, resurrects
  suggestions from the wrong prefix. Model it as `cursor = None` and check the
  sentinel before every hop.
- **But the buffer keeps growing.** The characters after the prefix died still
  belong to the sentence being typed, because `'#'` must commit the *whole*
  thing — including the part that had no matches. Losing them is the second
  bug, and it only shows up on the query after the commit.
- **`'#'` returns `[]`, not the suggestions.** And it must reset both the
  buffer and the cursor.
- **Committing updates every node on the path**, not just the terminal — that
  is the invariant that makes rule 1's node maps correct. A newly committed
  sentence creates whatever nodes it needs.
- **Ties are ASCII, so a leading space ranks first.** `"i love leetcode"` beats
  `"iroman"` at equal counts because `' ' < 'r'`. Python's default string
  comparison already does this; do not "helpfully" strip or normalise.
- **Fewer than three matches** returns one or two, and none returns `[]`.
- **Scale follow-up:** caching a precomputed top-3 on each node makes a
  keystroke O(1) but makes each commit O(L) *merges* — worth it when the
  history is nearly static, wrong when it is a live feed, since a count bump
  can invalidate a cached list arbitrarily far up the path.
""",
        ),
    ],
}

class TrieNode:
    __slots__ = ("children", "counts")

    def __init__(self) -> None:
        self.children: dict[str, TrieNode] = {}
        self.counts: dict[str, int] = {}  # sentence -> count, for every sentence below


class AutocompleteSystem:
    def __init__(self, sentences: list[str], times: list[int]) -> None:
        self.root = TrieNode()
        self.buffer = ""
        self.cursor: TrieNode | None = self.root
        for sentence, count in zip(sentences, times, strict=True):
            self._add(sentence, count)

    def _add(self, sentence: str, count: int) -> None:
        node = self.root
        for character in sentence:
            node = node.children.setdefault(character, TrieNode())
            node.counts[sentence] = node.counts.get(sentence, 0) + count

    def input(self, character: str) -> list[str]:
        if character == "#":
            self._add(self.buffer, 1)
            self.buffer = ""
            self.cursor = self.root
            return []

        self.buffer += character  # grows even after the prefix dies
        if self.cursor is not None:
            self.cursor = self.cursor.children.get(character)
        if self.cursor is None:
            return []

        ranked = nsmallest(3, self.cursor.counts.items(), key=lambda kv: (-kv[1], kv[0]))
        return [sentence for sentence, _ in ranked]


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    system = AutocompleteSystem(
        ["i love you", "island", "iroman", "i love leetcode"], [5, 3, 2, 2]
    )

    # Tie at count 2: " " (32) < "r" (114), so "i love leetcode" outranks "iroman".
    assert system.input("i") == ["i love you", "island", "i love leetcode"]
    assert system.input(" ") == ["i love you", "i love leetcode"]
    assert system.input("a") == []  # prefix "i a" is dead
    assert system.input("#") == []  # commits "i a" with count 1

    # The dead tail was still buffered, so "i a" is now history.
    assert system.input("i") == ["i love you", "island", "i love leetcode"]
    assert system.input(" ") == ["i love you", "i love leetcode", "i a"]
    assert system.input("a") == ["i a"]
    assert system.input("#") == []  # "i a" now has count 2

    # Count 2 pushes "i a" above the other count-2 entries: "i a" < "i love ..."
    # and < "iroman" on ASCII order.
    assert system.input("i") == ["i love you", "island", "i a"]
    assert system.input(" ") == ["i love you", "i a", "i love leetcode"]
    assert system.input("#") == []

    # Re-check that ranking explicitly: "i " candidates are
    # "i love you" 5, "i a" 2, "i love leetcode" 2.
    fresh = AutocompleteSystem(
        ["i love you", "island", "iroman", "i love leetcode", "i a"], [5, 3, 2, 2, 2]
    )
    assert fresh.input("i") == ["i love you", "island", "i a"]
    assert fresh.input(" ") == ["i love you", "i a", "i love leetcode"]
    assert fresh.input("l") == ["i love you", "i love leetcode"]
    assert fresh.input("o") == ["i love you", "i love leetcode"]
    assert fresh.input("z") == []
    assert fresh.input("z") == []  # still dead, not resurrected
    assert fresh.input("#") == []  # commits "i lozz", dead tail included

    # "i lozz" is now history, so the same keystrokes surface it.
    assert fresh.input("i") == ["i love you", "island", "i a"]
    assert fresh.input(" ") == ["i love you", "i a", "i love leetcode"]
    assert fresh.input("l") == ["i love you", "i love leetcode", "i lozz"]
    assert fresh.input("o") == ["i love you", "i love leetcode", "i lozz"]
    assert fresh.input("z") == ["i lozz"]
    assert fresh.input("#") == []

    # Empty history: everything is [] until something is committed.
    empty = AutocompleteSystem([], [])
    assert empty.input("a") == []
    assert empty.input("b") == []
    assert empty.input("#") == []
    assert empty.input("a") == ["ab"]
    assert empty.input("b") == ["ab"]
    assert empty.input("c") == []

    # Fewer than three matches, and a sentence that is a prefix of another.
    nested = AutocompleteSystem(["ab", "abc", "abcd"], [1, 1, 1])
    assert nested.input("a") == ["ab", "abc", "abcd"]
    assert nested.input("b") == ["ab", "abc", "abcd"]
    assert nested.input("c") == ["abc", "abcd"]
    assert nested.input("d") == ["abcd"]
    assert nested.input("#") == []

    # Pure count ordering beats alphabetical.
    counts = AutocompleteSystem(["zz", "yy", "xx"], [9, 5, 1])
    assert counts.input("z") == ["zz"]
    assert counts.input("#") == []
    assert counts.input("y") == ["yy"]
    assert counts.input("#") == []

    # Committing an existing sentence bumps it rather than duplicating it.
    bump = AutocompleteSystem(["ba", "bb"], [1, 2])
    assert bump.input("b") == ["bb", "ba"]
    assert bump.input("a") == ["ba"]
    assert bump.input("#") == []
    assert bump.input("b") == ["ba", "bb"]  # "ba" is now 2 and sorts first on the tie
    assert bump.input("#") == []
