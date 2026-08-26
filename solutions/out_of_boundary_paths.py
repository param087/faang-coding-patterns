"""Out of Boundary Paths — LeetCode 576."""

from __future__ import annotations

from functools import cache

META = {
    "pattern": "dp-grid-knapsack",
    "insight": "Count paths that leave rather than positions that stay: a move off the edge banks a path immediately and never re-enters the grid.",
    "time": "O(maxMove · m · n)",
    "space": "O(m · n)",
    "sections": [
        (
            "What it asks",
            """
A ball starts at `(startRow, startColumn)` in an `m × n` grid. Each move takes
it one cell up, down, left or right, and it may make **at most** `maxMove`
moves. Count the move sequences that take it out of the grid, modulo 1e9+7.

Ask whether paths that leave earlier and later are distinct (yes — a path is a
sequence of moves, and it ends the moment the ball is out). Constraints are
`m, n ≤ 50`, `maxMove ≤ 50`, so 125 000 states.
""",
        ),
        (
            "The insight",
            """
Branching four ways for up to 50 moves is 4⁵⁰ ≈ 1.3 × 10³⁰ sequences. But the
future depends only on `(moves left, row, column)`, so the count collapses to a
table of 50 × 50 × 50.

Sweep forwards over move number:

> `grid[r][c]` = how many distinct move sequences leave the ball on `(r, c)`
> after the moves made so far.

Each step, every cell distributes its count to its four neighbours. A neighbour
inside the grid lands in the next layer; a neighbour outside is a **finished
path** and is added straight to a running total.

Start with `1` at the source and run `maxMove` layers. The running total is the
answer — "at most `maxMove` moves" needs no special handling, because a path
that escapes on move 3 was banked at layer 3 and contributes nothing afterwards.
""",
        ),
        (
            "Pitfall: escapes are absorbing",
            """
The bug that survives testing on the samples is letting escaped paths keep
moving — for instance by treating the outside as a cell, or by re-adding the
running total at every subsequent layer. On `1 × 1` with `maxMove = 1` the
answer is 4; that same grid with `maxMove = 3` is **still 4**, because the ball
is gone after its first move. A version that lets escapes propagate reports 4,
16 or 64 depending on the exact mistake, and all three look plausible.

The mirror mistake is counting survivors: computing how many sequences remain
inside and subtracting. There is nothing to subtract from — after `maxMove`
moves the sequences are not `4^maxMove` minus the survivors, since escaped paths
stop early and never branch again.

Take the modulo on the running total as well as on the cells. It is easy to
reduce `grid[r][c]` diligently and let `escaped` grow unbounded, which is only a
performance bug in Python but an overflow in Java or C++.
""",
        ),
    ],
}

MOD = 10**9 + 7
STEPS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def find_paths(rows: int, cols: int, max_move: int, start_row: int, start_col: int) -> int:
    counts = [[0] * cols for _ in range(rows)]
    counts[start_row][start_col] = 1
    escaped = 0

    for _ in range(max_move):
        nxt = [[0] * cols for _ in range(rows)]
        for r in range(rows):
            for c in range(cols):
                ways = counts[r][c]
                if not ways:
                    continue
                for dr, dc in STEPS:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        nxt[nr][nc] = (nxt[nr][nc] + ways) % MOD
                    else:
                        escaped = (escaped + ways) % MOD  # banked, never moves again
        counts = nxt

    return escaped


def find_paths_topdown(
    rows: int, cols: int, max_move: int, start_row: int, start_col: int
) -> int:
    """The same recurrence read backwards — memoised, for contrast."""

    @cache
    def ways(moves_left: int, r: int, c: int) -> int:
        if not (0 <= r < rows and 0 <= c < cols):
            return 1  # already out: exactly one way, and it is finished
        if moves_left == 0:
            return 0
        return sum(ways(moves_left - 1, r + dr, c + dc) for dr, dc in STEPS) % MOD

    result = ways(max_move, start_row, start_col)
    ways.cache_clear()
    return result


CASES = [
    ((2, 2, 2, 0, 0), 6),
    ((1, 3, 3, 0, 1), 12),
    ((1, 1, 1, 0, 0), 4),
    ((1, 1, 3, 0, 0), 4),  # the ball is gone after move 1; extra moves add nothing
    ((2, 2, 0, 0, 0), 0),  # no moves allowed, so nothing escapes
    ((3, 3, 4, 1, 1), 52),
    ((2, 3, 5, 1, 2), 78),
    ((8, 50, 23, 5, 26), 914783380),  # large enough that the modulo matters
]


def solve(rows: int, cols: int, max_move: int, start_row: int, start_col: int) -> int:
    return find_paths(rows, cols, max_move, start_row, start_col)


def check() -> None:
    for args, expected in CASES:
        assert find_paths(*args) == expected, args
        # Bottom-up and top-down must agree.
        assert find_paths_topdown(*args) == expected, args
