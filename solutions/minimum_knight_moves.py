"""Minimum Knight Moves — LeetCode 1197 (Premium)."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "graph-traversal",
    "insight": "Fold the target into the first quadrant by symmetry and cap the board just past it; the infinite plane collapses to O(xy) cells.",
    "time": "O(|x| · |y|)",
    "space": "O(|x| · |y|)",
    "sections": [
        (
            "What it asks",
            """
LeetCode 1197 is premium, so the statement is not public — the task in my own
words: a knight starts at `(0, 0)` on an **infinite** chessboard and moves in
the usual L. Given a target `(x, y)`, return the fewest moves to land on it.
It is always reachable, so there is no −1 branch.

The clarifying question is about the board: infinite in all four directions,
or a quadrant? Infinite is what makes the naive BFS blow up, and it is also
what makes the symmetry argument legal.
""",
        ),
        (
            "The insight",
            """
Every move costs 1, so it is BFS — but on an infinite plane a plain BFS to a
target 300 squares away explores a disc of radius ~300 in *all* directions,
roughly 8·|x|·|y| worth of cells with nothing stopping the frontier drifting
away from the goal. Two cuts fix it.

**Symmetry.** The move set is closed under negating either coordinate and
under swapping them, so the distance to `(x, y)` equals the distance to
`(|x|, |y|)`. Take absolute values on entry and you have thrown away three
quadrants before the first pop.

**A window.** An optimal path never needs to run far past the target or far
behind the origin. Clamping to `-2 ≤ nx ≤ x + 2` (same for `y`) keeps the
search inside a rectangle of `(x + 5)(y + 5)` cells. The slack of 2 is not
cosmetic — it is exactly what the two exceptions below need.
""",
        ),
        (
            "The two exceptions that kill the closed form",
            """
There is a well-known O(1) formula, and everyone who writes it from memory
gets `(1, 1)` and `(2, 2)` wrong.

- `(1, 1)` looks adjacent; it takes **2** moves — out to `(2, -1)` and back.
- `(2, 2)` takes **4**, not 2: no pair of knight moves sums to `(2, 2)`.

Both fixes require stepping *negative* or *past* the target, which is why the
pruning window has slack on both ends rather than clamping at 0. Clamp at
`nx >= 0` and `(1, 1)` returns 4 or loops forever.

Two more worth stating out loud: `(0, 0)` is 0 moves, and `(1, 0)` is **3**,
not 1. Put all four in your test list before you claim the formula.

Follow-up, if they push on the 300×300 bound: **bidirectional BFS** halves the
exponent, and beyond that the closed form (a linear function of `x` and `y`
with those small-case patches) is O(1).
""",
        ),
    ],
}

KNIGHT_MOVES = ((1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2))


def min_knight_moves(x: int, y: int) -> int:
    # Symmetry: the move set is closed under sign flips, so fold to quadrant one.
    x, y = abs(x), abs(y)
    if (x, y) == (0, 0):
        return 0

    visited = {(0, 0)}
    queue: deque[tuple[int, int]] = deque([(0, 0)])
    moves = 0

    while queue:
        moves += 1
        for _ in range(len(queue)):
            cr, cc = queue.popleft()
            for dr, dc in KNIGHT_MOVES:
                nr, nc = cr + dr, cc + dc
                if (nr, nc) == (x, y):
                    return moves
                # Slack of 2 on both ends: (1,1) and (2,2) need to step outside.
                if not (-2 <= nr <= x + 2 and -2 <= nc <= y + 2):
                    continue
                if (nr, nc) in visited:
                    continue
                visited.add((nr, nc))
                queue.append((nr, nc))

    return -1  # unreachable on an infinite board, kept only for total safety


CASES = [
    ((0, 0), 0),
    ((2, 1), 1),
    ((1, 0), 3),  # not 1 — the shortest hop is a three-move detour
    ((1, 1), 2),  # exception one
    ((2, 2), 4),  # exception two
    ((5, 5), 4),
    ((-5, -5), 4),  # symmetry: same answer in the third quadrant
    ((-3, 8), 5),
]


def solve(x: int, y: int) -> int:
    return min_knight_moves(x, y)
