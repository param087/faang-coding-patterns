"""Word Search II — LeetCode 212."""

from __future__ import annotations

META = {
    "pattern": "tries",
    "insight": "Drive one DFS over the board with the trie instead of running one DFS per word, so a dead prefix kills every word behind it at once.",
    "time": "O(m·n·4·3^(L-1)) worst case, L the longest word; O(total word chars) to build the trie",
    "space": "O(total word chars) for the trie, O(L) recursion",
    "sections": [
        (
            "What it asks",
            """
Given an `m × n` board of letters and a word list, return every word that can
be spelled by walking to orthogonally adjacent cells without reusing a cell
within one word.

Clarify: **cells are reusable across different words** (only within a single
word are they forbidden), the output order is free, and duplicates in `words`
should not produce duplicates in the output. Also ask the sizes — they are the
whole design: board up to 12 × 12, but **up to 3 × 10⁴ words** of length ≤ 10.
The word list is two orders of magnitude bigger than the board, which tells you
immediately which one you are allowed to loop over.
""",
        ),
        (
            "Brute force, and why it fails",
            """
Solve Word Search I once per word: for each word, start a DFS from every cell.

One DFS is roughly `m·n·4·3^(L-1)` — at 12 × 12 and L = 10 that is
144 · 4 · 3⁹ ≈ 1.1 × 10⁷. Multiply by 3 × 10⁴ words and you are at
**3 × 10¹¹ operations**. Dead on the clock, and dead for the obvious reason:
if the board has no cell starting with `z`, you re-derive that fact separately
for all 1 100 words beginning with `z`.
""",
        ),
        (
            "The insight",
            """
Invert the loop. Walk the **board** once and let a trie of the word list say,
at each step, whether any word still has this path as a prefix.

The DFS carries a trie node alongside `(row, col)`. Stepping onto a neighbour
is legal only if that letter is a child of the current node — so the moment a
prefix goes dead, **every word sharing it is pruned in one branch cut**, which
is exactly the redundancy the brute force pays for over and over.

Store the whole word on its terminal node rather than an `is_word` flag. When
the DFS lands on a terminal node the answer is right there, with no string
built by concatenation on the way down and no path list to join.

Deduplication is free: set the stored word to `None` after collecting it. That
handles both a duplicated entry in `words` and the same word being spellable
along two different paths.
""",
        ),
        (
            "The pruning that decides it",
            """
The trie alone is not enough for the adversarial test — the one with a board of
all `a` and words like `"aaaaaaaaaa"`. Two more moves are what actually make it
pass:

1. **Prune exhausted branches.** After the recursion for a child returns, if
   that child node has no children left and no word on it, delete it from its
   parent. The trie shrinks as words are found, so a board of identical letters
   stops re-exploring paths whose words are all already collected. Without
   this, the same test times out with the trie in place.
2. **Mark visited in the board itself.** Overwrite the cell with a sentinel
   (`"#"`) before recursing and restore it after. A `set` of coordinates works
   but costs a hash per step; the sentinel costs a store. The restore must be
   in the unwinding path of *every* return, which is why the swap brackets the
   recursion rather than sitting inside an `if`.

The second half of rule 1 is the subtle part: you may only delete a node once
its subtree is genuinely spent. Checking `not child.children and child.word is
None` after the recursive call is precisely that condition.
""",
        ),
        (
            "Dry run",
            """
Board

```
o a a n
e t a e
i h k r
i f l v
```

with `words = ["oath", "pea", "eat", "rain"]`.

- Build the trie. The root has children `o`, `p`, `e`, `r`.
- Scan cells. `(0,0) = 'o'` is a child of the root, so descend: `a` → `t` → `h`
  at `(2,1)` carries the word **"oath"**. Collect it, blank the stored word.
- Unwinding, the `h` node has no children and no word, so it is deleted; then
  `t`, `a`, `o` go the same way. The entire `"oath"` branch is gone from the
  trie before the scan reaches column 1.
- `(0,1) = 'a'` is not a root child — one dict lookup, no DFS at all. Same for
  every `a`, `n`, `t`, `i`, `h`, `k`, `f`, `l`, `v` on the board.
- `(1,0) = 'e'` descends to `a` then needs `t`, but `(1,0)`'s neighbours give
  `t` at `(1,1)` — spelling **"eat"**? `e(1,0) → a` requires an adjacent `a`:
  `(0,0)` is `o`, `(2,0)` is `i`, `(1,1)` is `t`. Dead immediately.
- `(1,3) = 'e'` → `a` at `(1,2)` → `t` at `(1,1)`: **"eat"**.
- `"pea"` never starts: no `p` on the board, and it costs one failed lookup per
  cell rather than 144 DFS launches.

Result `["oath", "eat"]`.
""",
        ),
        (
            "Follow-ups",
            """
- **"What if the word list is fixed and boards stream in?"** Build the trie
  once outside the call. That is the real production shape, and it is why the
  trie belongs to the dictionary rather than to the query.
- **"What if the board is huge and the word list tiny?"** The inversion flips
  back: with 5 words on a 10⁶-cell board, per-word DFS from filtered start
  cells wins. Say which regime you are in; the answer is not unconditional.
- **Diagonal moves, or wrap-around** only changes the neighbour list — the trie
  half is untouched, which is the sign the decomposition is right.
- **Return the paths, not just the words.** Now you do need the coordinate
  list threaded through the recursion, and the `word`-on-node trick buys less.
- **Reusing a cell within a word** (Boggle-with-repeats) removes the visited
  marking and makes termination depend entirely on trie depth — which is fine,
  because words are bounded at 10.
""",
        ),
    ],
}


class TrieNode:
    __slots__ = ("children", "word")

    def __init__(self) -> None:
        self.children: dict[str, TrieNode] = {}
        self.word: str | None = None  # the whole word, not a flag


def find_words(board: list[list[str]], words: list[str]) -> list[str]:
    if not board or not board[0]:
        return []

    root = TrieNode()
    for word in words:
        node = root
        for character in word:
            node = node.children.setdefault(character, TrieNode())
        node.word = word

    rows, cols = len(board), len(board[0])
    found: list[str] = []

    def dfs(row: int, col: int, parent: TrieNode) -> None:
        character = board[row][col]
        node = parent.children.get(character)
        if node is None:
            return

        if node.word is not None:
            found.append(node.word)
            node.word = None  # dedupe: never collect the same word twice

        board[row][col] = "#"  # visited marker, restored below
        for next_row, next_col in (
            (row - 1, col),
            (row + 1, col),
            (row, col - 1),
            (row, col + 1),
        ):
            if 0 <= next_row < rows and 0 <= next_col < cols:
                dfs(next_row, next_col, node)
        board[row][col] = character

        # Prune a spent branch so identical-letter boards stop re-exploring it.
        if not node.children and node.word is None:
            del parent.children[character]

    for row in range(rows):
        for col in range(cols):
            dfs(row, col, root)

    return found


CASES = [
    (
        (
            [
                ["o", "a", "a", "n"],
                ["e", "t", "a", "e"],
                ["i", "h", "k", "r"],
                ["i", "f", "l", "v"],
            ],
            ["oath", "pea", "eat", "rain"],
        ),
        ["eat", "oath"],
    ),
    # "abdca" traces the whole 2x2 ring and then needs (0,0) again — illegal.
    (([["a", "b"], ["c", "d"]], ["abdca"]), []),
    (
        ([["a", "b"], ["c", "d"]], ["ab", "cd", "ac", "bd", "abdc", "adcb"]),
        ["ab", "abdc", "ac", "bd", "cd"],  # "adcb" has no d adjacent to a
    ),
    (([["a"]], ["a", "a", "aa", "b"]), ["a"]),  # duplicate entry must not duplicate output
    (
        (
            [["a", "a", "a"], ["a", "a", "a"], ["a", "a", "a"]],
            ["a", "aa", "aaa", "aaaa", "aaaaa", "aaaaaaaaaa"],
        ),
        ["a", "aa", "aaa", "aaaa", "aaaaa"],  # 10 a's needs 10 distinct cells; only 9 exist
    ),
    (([["a", "b"], ["c", "d"]], []), []),
    (([], ["ab"]), []),
]


def solve(board: list[list[str]], words: list[str]) -> list[str]:
    # The DFS marks visited cells in place, so copy: CASES are reused.
    return sorted(find_words([row[:] for row in board], words))
