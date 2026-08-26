"""Knight Probability in Chessboard — LeetCode 688."""

from __future__ import annotations

from fractions import Fraction

META = {
    "pattern": "dp-grid-knapsack",
    "insight": "Push probability mass forward over the board instead of enumerating 8^k move sequences; each step spreads every square eight ways.",
    "time": "O(k · n²) — eight transitions per cell",
    "space": "O(n²)",
    "sections": [
        (
            "What it asks",
            """
A knight starts at `(row, column)` on an `n × n` board and makes exactly `k`
moves, each one chosen **uniformly at random from the eight** knight moves —
including moves that take it off the board. Once off, it stops. Return the
probability it is still on the board after all `k` moves.

Ask whether the knight keeps moving after leaving (it does not — leaving is
final), and confirm "exactly `k` moves", not "at most". Constraints are
`n ≤ 25`, `k ≤ 100`, so a `k × n × n` table is 62 500 states.
""",
        ),
        (
            "The insight",
            """
The naive reading is a search over move sequences: 8^k of them, and at k = 100
that is 8¹⁰⁰ — not a number you can enumerate. But the sequences collapse: two
different routes that end on the same square after the same number of moves are
interchangeable from there on.

> `dp[r][c]` = the probability the knight is on square `(r, c)` after the moves
> made so far.

Seed `dp[row][column] = 1`, then repeat `k` times: every square hands out an
eighth of its mass to each of its eight targets, and mass aimed off the board is
simply dropped. The answer is the total mass left, `Σ dp`.

Dropping rather than tracking is the neat part — you never need an "off the
board" state, because the question only asks how much **stayed**.

Working forwards (push mass out) and backwards (`f(k, r, c)` = survival
probability from here, memoised) are both fine; the forward sweep is easier to
reason about and gives O(n²) space without a recursion limit.
""",
        ),
        (
            "Pitfall: divide by 8, not by the legal moves",
            """
The most common wrong answer normalises by the number of moves that stay on the
board. That is a different process — a knight that never falls off. From a
corner of an 8 × 8 board only 2 of the 8 moves are legal, so after one move the
correct answer is `2/8 = 0.25`, while the renormalised version says `1.0`.

Read the statement carefully: the knight "chooses one of eight moves", and an
off-board choice ends the walk. Always `/ 8`.

Two smaller traps:

- `k = 0` must return **1.0**, and a start square is always on the board. A
  recursion that checks `k == 0` before checking bounds gets this right; one that
  checks in the other order still works, but only because the start is valid.
- The board is not automatically big enough for a knight. On `n = 3`, the centre
  square has **zero** legal moves — every one of the eight lands off. Any test
  set without a tiny board misses this.
""",
        ),
    ],
}

MOVES = (
    (1, 2),
    (2, 1),
    (2, -1),
    (1, -2),
    (-1, -2),
    (-2, -1),
    (-2, 1),
    (-1, 2),
)


def knight_probability(n: int, k: int, row: int, column: int) -> float:
    board = [[0.0] * n for _ in range(n)]
    board[row][column] = 1.0

    for _ in range(k):
        nxt = [[0.0] * n for _ in range(n)]
        for r in range(n):
            for c in range(n):
                mass = board[r][c]
                if mass == 0.0:
                    continue
                share = mass / 8  # always eight, even from a corner
                for dr, dc in MOVES:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < n and 0 <= nc < n:
                        nxt[nr][nc] += share
                    # else: the mass leaves the board and is never counted again
        board = nxt

    return sum(sum(row_probs) for row_probs in board)


def knight_probability_exact(n: int, k: int, row: int, column: int) -> Fraction:
    """The same walk in exact rationals — no floating point to argue about."""
    board = {(row, column): Fraction(1)}

    for _ in range(k):
        nxt: dict[tuple[int, int], Fraction] = {}
        for (r, c), mass in board.items():
            share = mass / 8
            for dr, dc in MOVES:
                nr, nc = r + dr, c + dc
                if 0 <= nr < n and 0 <= nc < n:
                    nxt[nr, nc] = nxt.get((nr, nc), Fraction(0)) + share
        board = nxt

    return sum(board.values(), Fraction(0))


CASES = [
    ((3, 2, 0, 0), 0.0625),
    ((1, 0, 0, 0), 1.0),  # zero moves: still on the board, trivially
    ((1, 1, 0, 0), 0.0),  # a 1x1 board has no legal knight move at all
    ((3, 1, 1, 1), 0.0),  # the centre of a 3x3 board: all eight moves leave
    ((8, 1, 0, 0), 0.25),  # 2 of 8 from a corner — not 1.0
    ((4, 3, 0, 1), 0.058594),
    ((6, 5, 2, 2), 0.137207),
    ((8, 30, 3, 3), 0.000282),
]


def solve(n: int, k: int, row: int, column: int) -> float:
    return round(knight_probability(n, k, row, column), 6)


def check() -> None:
    for args, expected in CASES:
        assert solve(*args) == expected, args
        # The float DP must match the exact rational walk to 6 decimals.
        exact = knight_probability_exact(*args)
        assert round(float(exact), 6) == expected, args
