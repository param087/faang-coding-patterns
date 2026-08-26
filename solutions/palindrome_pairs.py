"""Palindrome Pairs — LeetCode 336."""

from __future__ import annotations

META = {
    "pattern": "tries",
    "insight": "words[i] + words[j] is a palindrome exactly when one word reverses the other's prefix and the leftover middle is itself a palindrome.",
    "time": "O(n·k²) — k the word length, for the trie build and every walk",
    "space": "O(n·k) for the trie plus its palindrome lists",
    "sections": [
        (
            "What it asks",
            """
Given distinct words, return every ordered pair of indices `(i, j)`, `i != j`,
such that `words[i] + words[j]` is a palindrome.

Ask whether the empty string can appear (**yes**, and it is the case that
breaks half of all submissions) and whether words repeat (no — LeetCode
guarantees distinct, which lets you key on index alone).

Brute force is n² concatenations of length 2k: at n = 5000, k = 300 that is
2.5·10⁷ pairs × 600 characters ≈ 10¹⁰ character comparisons.
""",
        ),
        (
            "The insight",
            """
Split by which word is longer. Write `A = words[i]`, `B = words[j]`, and let
the pair concatenate to a palindrome.

- **Equal lengths** — then `B` must be exactly `reverse(A)`.
- **`B` shorter** — `B` must reverse some *prefix* of `A`, and the rest of `A`
  (its tail) must be a palindrome in its own right: `A₁A₂ + reverse(A₁)` is a
  palindrome iff `A₂` is.
- **`B` longer** — mirror image: `A` must reverse a *suffix* of `B`, and the
  remaining head of `B` must be a palindrome.

All three are "match one string against the reverse of the other, then test
that the leftover is a palindrome". So insert every word **reversed** into a
trie, and at each node keep `below`: the indices of words whose *remaining*
reversed tail below that node is a palindrome. Then walking `words[i]` down the
trie reads off both shorter and longer partners in a single descent:

- hitting a node that terminates word `j` mid-walk → `B` is shorter; check that
  the unconsumed tail of `A` is a palindrome;
- reaching the end of `A` still inside the trie → every `j` in that node's
  `below` is a longer partner, already pre-verified.
""",
        ),
        (
            "The empty string, and the double count",
            """
Two traps, both of which produce a *nearly* right answer.

**The empty string.** `""` pairs with every palindrome in the list, in **both**
orders. The trie handles it without a special case only because `""` sits at the
root: walking any palindromic word `A` checks `root.index` at step 0 with the
whole of `A` as leftover, and walking `""` itself falls straight through to
`root.below`. If you special-case shorter-partner logic to `k ≥ 1`, you lose
`("aba", "")` and get a wrong answer on a test you cannot see.

**Double counting.** The equal-length case is reachable from both the
"partner is shorter" and "partner is longer" branches. Pick one owner: check
`node.index` only for `k < len(A)` (strictly shorter partners) and let
`below` — which includes the word ending at that very node, its leftover being
the empty string, a palindrome — own everything from `len(A)` on. Get that
boundary wrong and `["abcd", "dcba"]` reports each pair twice.

Guarding with `j != i` is separate and still required: a palindrome pairs with
itself under this test, and `(i, i)` is not a valid answer.
""",
        ),
    ],
}


class _Node:
    __slots__ = ("below", "children", "index")

    def __init__(self) -> None:
        self.children: dict[str, _Node] = {}
        self.index = -1  # word that terminates here, -1 for none
        self.below: list[int] = []  # words whose remaining tail below here is a palindrome


def _is_palindrome(word: str, low: int, high: int) -> bool:
    while low < high:
        if word[low] != word[high]:
            return False
        low += 1
        high -= 1
    return True


def palindrome_pairs(words: list[str]) -> list[list[int]]:
    root = _Node()

    for index, word in enumerate(words):
        node = root
        length = len(word)
        for depth, char in enumerate(reversed(word)):
            # word[:length - depth] is what is left below; palindromic tails
            # are exactly the longer partners we will want on the way down.
            if _is_palindrome(word, 0, length - depth - 1):
                node.below.append(index)
            node = node.children.setdefault(char, _Node())
        node.below.append(index)  # empty leftover is a palindrome
        node.index = index

    pairs: list[list[int]] = []
    for index, word in enumerate(words):
        node = root
        for cut, char in enumerate(word):
            # Partner strictly shorter: it ends here, the rest of `word` must
            # be a palindrome on its own.
            partner = node.index
            if partner != -1 and partner != index and _is_palindrome(word, cut, len(word) - 1):
                pairs.append([index, partner])
            child = node.children.get(char)
            if child is None:
                break
            node = child
        else:
            # Consumed all of `word`: every pre-verified partner below is valid.
            pairs.extend([index, other] for other in node.below if other != index)

    return pairs


CASES = [
    ((["abcd", "dcba", "lls", "s", "sssll"],), [[0, 1], [1, 0], [2, 4], [3, 2]]),
    ((["bat", "tab", "cat"],), [[0, 1], [1, 0]]),
    # The empty string pairs with every palindrome, both ways round.
    ((["abc", "cba", "", "aba"],), [[0, 1], [1, 0], [2, 3], [3, 2]]),
    ((["a", ""],), [[0, 1], [1, 0]]),
    # Equal lengths: reachable from both branches, so exactly one owner.
    ((["ab", "ba", ""],), [[0, 1], [1, 0]]),
    # One word with several partners of different lengths, in both directions.
    ((["race", "car", "ecar", "racecar", ""],), [[0, 1], [0, 2], [2, 0], [3, 4], [4, 3]]),
    ((["a"],), []),  # a palindrome pairs with itself under the test; j != i must reject it
    (([],), []),
]


def solve(words: list[str]) -> list[list[int]]:
    return sorted(palindrome_pairs(words))  # any order is accepted; sort to compare
