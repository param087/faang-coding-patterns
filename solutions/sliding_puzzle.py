"""Sliding Puzzle — LeetCode 773."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "graph-traversal",
    "insight": "Flatten the board to a six-character string and BFS the 360 reachable states; a board is a graph node, not a grid.",
    "time": "O(6! · 6) — the state space, independent of any input size",
    "space": "O(6!)",
    "sections": [
        (
            "What it asks",
            """
A 2×3 board holding the tiles `1`–`5` and one blank, written `0`. A move
swaps the blank with an orthogonally adjacent tile. Return the fewest moves to
reach

```
1 2 3
4 5 0
```

or −1 if it is impossible.

Worth asking whether the board size is fixed at 2×3. It is, and that
constraint is the whole reason brute-force BFS is the intended answer rather
than a cop-out.
""",
        ),
        (
            "The insight",
            """
The node is not a cell — the node is the **entire board**. Six positions, six
distinct symbols, so `6! = 720` states, of which exactly half are reachable
from any given start. 360 nodes with degree ≤ 3 is a graph you can search
exhaustively before the interviewer finishes reading your variable names.

Two moves make it concrete:

1. **Flatten to a string.** `"123450"` is hashable, comparable to the target
   in one `==`, and slices cheaply. Nested lists need a `tuple(map(tuple, …))`
   dance every time you want to put one in a set.
2. **Hard-code adjacency on the flat index.** Index `i` in the flattened board
   sits at row `i // 3`, column `i % 3`, and its neighbours are a fixed table:
   `{0: (1, 3), 1: (0, 2, 4), 2: (1, 5), 3: (0, 4), 4: (1, 3, 5), 5: (2, 4)}`.
   Deriving that table on the spot is faster and less error-prone than writing
   a 2D bounds check for a board this small.

Then it is textbook BFS with a level counter, because every move costs 1.
""",
        ),
        (
            "Follow-ups",
            """
- **Why −1 ever happens.** Permutation **parity** is invariant: a blank move
  is a transposition, and moving the blank back to its home square always
  takes an even number of them on this board. So the 720 permutations split
  into two orbits of 360 and half of all boards can never be solved.
  `[[1,2,3],[5,4,0]]` is the canonical unsolvable one — a single swap away
  from the goal, and unreachable. If you only need *solvable or not*, count
  inversions in O(n) rather than searching.
- **The 3×3 8-puzzle.** `9!/2 = 181 440` still fits in BFS, but it is the
  natural point to switch to **A\\*** with the sum of Manhattan distances, or
  IDA\\*, which is what actual solvers use.
- **The 4×4 15-puzzle.** `16!/2 ≈ 10¹³` — BFS is dead. A\\* with a pattern
  database, or bidirectional BFS if you insist on uninformed search.
- **Bidirectional BFS** is the cheap win at any size: the goal state is
  known, so expand from both ends and meet in the middle.
""",
        ),
    ],
}

TARGET = "123450"
# Neighbours of each flattened index on a 2x3 board — a table beats bounds checks.
ADJACENT = {0: (1, 3), 1: (0, 2, 4), 2: (1, 5), 3: (0, 4), 4: (1, 3, 5), 5: (2, 4)}


def sliding_puzzle(board: list[list[int]]) -> int:
    start = "".join(str(tile) for row in board for tile in row)
    if start == TARGET:
        return 0

    seen = {start}
    queue: deque[str] = deque([start])
    moves = 0

    while queue:
        moves += 1
        for _ in range(len(queue)):
            state = queue.popleft()
            blank = state.index("0")
            for swap in ADJACENT[blank]:
                chars = list(state)
                chars[blank], chars[swap] = chars[swap], chars[blank]
                nxt = "".join(chars)
                if nxt == TARGET:
                    return moves
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)

    return -1  # the start sits in the unreachable half of the parity split


CASES = [
    (([[1, 2, 3], [4, 5, 0]],), 0),
    (([[1, 2, 3], [4, 0, 5]],), 1),
    (([[1, 2, 3], [0, 4, 5]],), 2),
    (([[1, 2, 3], [5, 4, 0]],), -1),  # wrong parity orbit: one swap, never reachable
    (([[4, 1, 2], [5, 0, 3]],), 5),
    (([[0, 1, 2], [4, 5, 3]],), 3),
    (([[3, 2, 4], [1, 5, 0]],), 14),
    (([[5, 4, 3], [2, 1, 0]],), 14),  # the reversed board, at the far end of the orbit
]


def solve(board: list[list[int]]) -> int:
    return sliding_puzzle([row[:] for row in board])
