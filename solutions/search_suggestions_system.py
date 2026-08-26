"""Search Suggestions System — LeetCode 1268."""

from __future__ import annotations

from bisect import bisect_left

META = {
    "pattern": "tries",
    "insight": "Sort the products first, then the three answers for every prefix are already adjacent — cache them on each trie node during insertion.",
    "time": "O(P log P + total product chars) to build, O(len(searchWord)) to answer everything",
    "space": "O(total product chars) — each node caches at most 3 strings",
    "sections": [
        (
            "What it asks",
            """
After each character typed of `searchWord`, return up to three products that
have the typed prefix, lexicographically smallest first. The output has exactly
`len(searchWord)` rows, one per prefix length 1..n — including empty rows for
prefixes nobody matches.

Clarify: products may repeat in the input (LeetCode says they are distinct, but
ask), and "at most three" means shorter rows are fine, not padded rows. The
sizes matter: 1000 products, total 2 × 10⁴ characters, `searchWord` ≤ 1000, so
even the naive filter is not going to blow up — the question is about the
*shape* of the answer, not about surviving the constraints.
""",
        ),
        (
            "The insight",
            """
Sorting is the move, and it is the move for both good solutions.

Once `products` is sorted, all strings sharing a prefix form a **contiguous
block**, and the three you want are the first three of that block. That single
fact gives two answers:

- **Trie.** Insert the sorted products; as each one walks down, append it to
  every node on its path that still holds fewer than three. When the typing
  walk reaches a node, its cached list *is* the answer — O(1) per keystroke
  after an O(1) step. Insertion order guarantees lexicographic order for free,
  so there is no sorting inside a node and no heap.
- **Binary search.** `bisect_left` for the prefix, then take up to three
  entries from there while they still start with the prefix. Ten lines, no
  data structure, and genuinely the better answer if this runs once.

Which to write depends on a question worth asking: **is the product catalogue
fixed and queried many times?** If yes, the trie amortises its build across
millions of queries and each keystroke is a pointer hop; if it is one shot, the
binary search wins on both time and the interviewer's patience. Write the trie
here — the pattern is tries — and name the binary search as the alternative.

The one keystroke-level detail: keep a *cursor* into the trie rather than
re-walking the prefix from the root each time. That is what makes the whole
sequence O(len(searchWord)) instead of O(len(searchWord)²).
""",
        ),
        (
            "Edge cases",
            """
- **The prefix goes dead mid-word.** Once the walk falls off the trie, every
  remaining row is empty — and must still be *emitted*. Returning early leaves
  a short result and is the most common failure here. Track a `None` cursor and
  keep looping.
- **A prefix that is itself a product.** `"mouse"` typed against a catalogue
  containing `"mouse"` and `"mousepad"` returns both; the node's cache holds
  strings that pass through *and* end at it.
- **Fewer than three matches.** Emit one or two; do not pad.
- **A single product**, or a `searchWord` longer than every product: rows go
  full, then empty, and never come back.
- **Duplicates in `products`**, if the interviewer allows them: the cache will
  happily hold the same string three times. Deduplicate during the sort
  (`sorted(set(products))`) rather than while querying.
- **"Top 3 by popularity, not alphabetically"** breaks the trick entirely — the
  contiguity argument is about lexicographic order. Then each node needs a
  score-ordered top-3 maintained on insert, which is LeetCode 642.
""",
        ),
    ],
}


class TrieNode:
    __slots__ = ("children", "top")

    def __init__(self) -> None:
        self.children: dict[str, TrieNode] = {}
        self.top: list[str] = []  # at most 3, already in lexicographic order


def suggested_products(products: list[str], search_word: str) -> list[list[str]]:
    root = TrieNode()
    for product in sorted(products):  # sorted insertion == sorted caches
        node = root
        for character in product:
            node = node.children.setdefault(character, TrieNode())
            if len(node.top) < 3:
                node.top.append(product)

    result: list[list[str]] = []
    cursor: TrieNode | None = root  # a cursor, not a re-walk from the root
    for character in search_word:
        cursor = cursor.children.get(character) if cursor is not None else None
        result.append(list(cursor.top) if cursor is not None else [])  # never break early
    return result


def suggested_products_bisect(products: list[str], search_word: str) -> list[list[str]]:
    """The one-shot alternative: sorted products, then a binary search per prefix."""
    ordered = sorted(products)
    result: list[list[str]] = []
    prefix = ""
    for character in search_word:
        prefix += character
        start = bisect_left(ordered, prefix)
        window = ordered[start : start + 3]
        result.append([word for word in window if word.startswith(prefix)])
    return result


CASES = [
    (
        (["mobile", "mouse", "moneypot", "monitor", "mousepad"], "mouse"),
        [
            ["mobile", "moneypot", "monitor"],
            ["mobile", "moneypot", "monitor"],
            ["mouse", "mousepad"],
            ["mouse", "mousepad"],
            ["mouse", "mousepad"],
        ],
    ),
    ((["havana"], "havana"), [["havana"]] * 6),
    # The prefix dies at "hav" and every later row must still be emitted.
    (
        (["bags", "baggage", "banner", "box", "cloths"], "bags"),
        [
            ["baggage", "bags", "banner"],
            ["baggage", "bags", "banner"],
            ["baggage", "bags"],
            ["bags"],
        ],
    ),
    ((["havana"], "tatiana"), [[], [], [], [], [], [], []]),
    # A product that is a strict prefix of another.
    ((["a", "ab", "abc"], "abcd"), [["a", "ab", "abc"], ["ab", "abc"], ["abc"], []]),
    # Search word longer than everything: rows go empty and stay empty.
    ((["code"], "codex"), [["code"], ["code"], ["code"], ["code"], []]),
    ((["zzz", "aaa", "mmm", "bbb"], "z"), [["zzz"]]),
    (([], "abc"), [[], [], []]),
]


def solve(products: list[str], search_word: str) -> list[list[str]]:
    trie_answer = suggested_products(products, search_word)
    assert trie_answer == suggested_products_bisect(products, search_word)
    return trie_answer
