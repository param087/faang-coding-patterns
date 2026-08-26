"""Design Tic-Tac-Toe — LeetCode 348."""

from __future__ import annotations

META = {
    "pattern": "matrix",
    "symbol": "TicTacToe",
    "insight": "Never store the board: give player 1 the value +1 and player 2 the value -1, and a line wins exactly when its running sum hits ±n.",
    "time": "O(1) per move, O(n) to construct",
    "space": "O(n) — 2n + 2 counters, not n² cells",
    "sections": [
        (
            "What it asks",
            """
This one is **premium**, so the statement is not public — described here in my
own words.

Design a class for an `n × n` tic-tac-toe board:

- `TicTacToe(n)` — an empty board.
- `move(row, col, player)` — player 1 or 2 marks an empty cell, and the call
  returns the winning player (`1` or `2`) if that move completed a full row,
  column, or either diagonal, otherwise `0`.

Ask what the caller guarantees, because it decides how much defensive code
belongs here: moves are valid and never replay a cell, players alternate, and
nobody calls `move` after a win. Also ask whether **n is bounded** — for
n = 3 nothing matters, but the whole point of the question is the caller who
says n = 10⁵ and streams a million moves.
""",
        ),
        (
            "The insight",
            """
The obvious design keeps an `n × n` grid and, after each move, re-scans the
row, the column and the diagonals: O(n) per move, O(n²) memory. At n = 10⁵
that is a 10¹⁰-cell board you cannot even allocate, so the grid has to go
before the scan does.

Nothing about the *board* is needed — only how close each of the `2n + 2` lines
is to being complete. Keep one running total per line and let the two players
push it in opposite directions:

> Player 1 adds **+1**, player 2 adds **−1**. A line is won exactly when its
> total reaches **+n** or **−n**.

The signed encoding is what makes a single integer enough. Two separate
per-player counters would work too, but they double the state and the `abs`
check disappears — the sign already tells you who won, which is why `move` can
simply `return player`.

A move touches at most four totals: `rows[row]`, `cols[col]`, and the
diagonals if `row == col` or `row + col == n - 1`. That is O(1) work and O(n)
space, and it never gets worse as the game goes on.
""",
        ),
        (
            "Edge cases, and what breaks the trick",
            """
- **n = 1.** One cell, and it lies on *both* diagonals — `row == col` and
  `row + col == n - 1` are both true at `(0, 0)`. The first move sets all four
  totals to ±1, `abs(...) == 1 == n`, and it wins. Correct, and it falls out
  without a special case; check it out loud rather than hand-waving.
- **The anti-diagonal test is `row + col == n - 1`, not `row + col == n`.**
  Off by one here and the anti-diagonal never fires on a 3×3 board, which is
  the only board most people test.
- **A contested line must go back to neutral.** Player 1 at `(0,0)` and player
  2 at `(0,1)` leaves `rows[0] == 0`, and a design counting "marks in this row"
  without the sign would call that row one step from a win. This is the case
  worth writing on the board.
- **Three players, or "which lines are still live?"** breaks the signed trick
  immediately: with three symbols there is no ordering of ±1 that separates
  them, so you fall back to a per-line `dict[player, count]` plus a flag for
  lines that are already contested and can never win.
- **Undo, or "return the winner at any time"** wants the last-move state kept
  as well; the counters are trivially reversible, so `undo` is the same four
  updates with the sign flipped.
""",
        ),
    ],
}


class TicTacToe:
    """An n x n board stored as 2n + 2 line totals, never as cells."""

    def __init__(self, n: int) -> None:
        self.n = n
        self.rows = [0] * n
        self.cols = [0] * n
        self.diagonal = 0
        self.anti_diagonal = 0

    def move(self, row: int, col: int, player: int) -> int:
        delta = 1 if player == 1 else -1

        self.rows[row] += delta
        self.cols[col] += delta
        if row == col:
            self.diagonal += delta
        if row + col == self.n - 1:  # not == n
            self.anti_diagonal += delta

        touched = (self.rows[row], self.cols[col], self.diagonal, self.anti_diagonal)
        return player if any(abs(total) == self.n for total in touched) else 0


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    # Row win, with the opponent interleaved so the totals get pushed both ways.
    game = TicTacToe(3)
    assert game.move(0, 0, 1) == 0
    assert game.move(1, 0, 2) == 0
    assert game.move(0, 1, 1) == 0
    assert game.move(1, 1, 2) == 0
    assert game.move(0, 2, 1) == 1  # top row complete

    # Column win for player 2.
    game = TicTacToe(3)
    assert game.move(0, 0, 1) == 0
    assert game.move(0, 2, 2) == 0
    assert game.move(1, 1, 1) == 0
    assert game.move(1, 2, 2) == 0
    assert game.move(2, 0, 1) == 0
    assert game.move(2, 2, 2) == 2

    # Main diagonal.
    game = TicTacToe(3)
    assert game.move(0, 0, 1) == 0
    assert game.move(0, 1, 2) == 0
    assert game.move(1, 1, 1) == 0
    assert game.move(0, 2, 2) == 0
    assert game.move(2, 2, 1) == 1

    # Anti-diagonal — the one that silently never fires if the test is `== n`.
    game = TicTacToe(3)
    assert game.move(0, 2, 1) == 0
    assert game.move(0, 0, 2) == 0
    assert game.move(1, 1, 1) == 0
    assert game.move(1, 0, 2) == 0
    assert game.move(2, 0, 1) == 1

    # n = 1: the single cell sits on both diagonals and wins immediately.
    assert TicTacToe(1).move(0, 0, 2) == 2

    # A contested row: full, but shared, so the signed total sits at 1, not 3.
    # An implementation counting "marks in this row" declares a win here.
    game = TicTacToe(3)
    assert game.move(0, 0, 1) == 0
    assert game.move(0, 1, 2) == 0
    assert game.rows[0] == 0
    assert game.move(0, 2, 1) == 0
    assert game.rows[0] == 1

    # A full 3x3 draw: every single call returns 0.
    #   X O X
    #   X O O
    #   O X X
    game = TicTacToe(3)
    draw = [
        (0, 0, 1),
        (0, 1, 2),
        (0, 2, 1),
        (1, 1, 2),
        (1, 0, 1),
        (1, 2, 2),
        (2, 1, 1),
        (2, 0, 2),
        (2, 2, 1),
    ]
    for r, c, p in draw:
        assert game.move(r, c, p) == 0, f"no line exists after ({r}, {c})"

    # A larger board, to show the cost does not depend on n.
    game = TicTacToe(1000)
    for i in range(999):
        assert game.move(i, i, 1) == 0
    assert game.move(999, 999, 1) == 1
