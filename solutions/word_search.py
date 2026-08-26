"""Word Search — LeetCode 79."""

from __future__ import annotations

from collections import Counter

META = {
    "pattern": "graph-traversal",
    "insight": "A cell is borrowed by the current path, not consumed by the search — mark it on the way in and restore it on the way out.",
    "time": "O(rows · cols · 3^len(word))",
    "space": "O(len(word)) for the recursion",
    "sections": [
        (
            "What it asks",
            """
Does `word` appear in the grid as a path of 4-directionally adjacent cells,
using no cell twice within that path?

Ask: can the same cell be reused (no — that restriction is the whole problem);
is the grid ASCII or Unicode (matters only for the pruning below); is `word`
ever empty; are we asked once or many times over the same board — if many, the
answer is Word Search II and a trie, not this.
""",
        ),
        (
            "The insight",
            """
This is a DFS over the grid graph, but with a crucial difference from island
counting: **visited is per path, not global**. A cell that is a dead end for
one path may be essential to another, so it must become available again when
the search backs out of it.

Hence the two lines around the recursion:

```python
board[r][c] = "#"       # borrow the cell for this path
found = any(dfs(...) for each direction)
board[r][c] = word[i]   # give it back
```

Restoring with `word[i]` is safe because the branch only got here after
`board[r][c] == word[i]`, so no separate copy of the character is needed. If
the interviewer objects to mutating the board, a `set` of coordinates
added before recursing and discarded after is the same algorithm.

Branching is 3, not 4: after the first step, one neighbour is always the cell
you came from, and it is marked. So the bound is O(rows · cols · 3^L).
""",
        ),
        (
            "Restore the cell, and prune the start",
            """
Forgetting the restore is the classic failure, and it fails *silently*: the
first exhausted branch permanently burns cells, so the search returns `False`
on boards where the word plainly exists. `"ABCB"` on the standard 3×4 board is
the case that catches you the other way — it must return `False`, because the
second `B` would need the cell the first one already occupies. Any solution
that returns `True` there has dropped the "no reuse" rule.

Two cheap prunes worth mentioning out loud:

- **Length.** If `len(word) > rows · cols`, return `False` before doing
  anything.
- **Which end to start from.** Count the board's letters. If the word's last
  letter is rarer on the board than its first, search for the word reversed —
  same answer, but far fewer doomed starting cells. On a board that is almost
  all `A` and the word `"AAAAAAAAAB"`, this turns near-exponential thrashing
  into a handful of probes, and interviewers notice.
""",
        ),
    ],
}

DIRECTIONS = ((0, 1), (1, 0), (0, -1), (-1, 0))


def exist(board: list[list[str]], word: str) -> bool:
    if not word:
        return True
    if not board or not board[0]:
        return False

    rows, cols = len(board), len(board[0])
    if len(word) > rows * cols:
        return False

    # Start from whichever end of the word is rarer on the board.
    counts = Counter(character for row in board for character in row)
    if counts[word[0]] > counts[word[-1]]:
        word = word[::-1]

    def dfs(r: int, c: int, i: int) -> bool:
        if i == len(word):
            return True
        if not (0 <= r < rows and 0 <= c < cols) or board[r][c] != word[i]:
            return False

        board[r][c] = "#"  # borrowed by this path only
        found = any(dfs(r + dr, c + dc, i + 1) for dr, dc in DIRECTIONS)
        board[r][c] = word[i]  # give it back on the way out
        return found

    return any(dfs(r, c, 0) for r in range(rows) for c in range(cols))


BOARD = [
    ["A", "B", "C", "E"],
    ["S", "F", "C", "S"],
    ["A", "D", "E", "E"],
]

CASES = [
    ((BOARD, "ABCCED"), True),
    ((BOARD, "SEE"), True),
    ((BOARD, "ABCB"), False),  # would have to reuse the first B
    ((BOARD, "ASADFCCE"), True),  # a long snaking path, up as well as down
    (([["A", "B"], ["C", "D"]], "ABDC"), True),
    (([["A", "B"], ["C", "D"]], "ABAD"), False),  # revisiting A is not allowed
    (([["A", "A"]], "AAA"), False),  # longer than the board
    (([["A"]], "A"), True),
    (([], "A"), False),
]


def solve(board: list[list[str]], word: str) -> bool:
    # Copy: exist marks cells mid-search, and CASES are reused across runs.
    return exist([row[:] for row in board], word)
