"""Sudoku Solver — LeetCode 37."""

from __future__ import annotations

META = {
    "pattern": "backtracking",
    "insight": "Keep row, column and box occupancy as bitmasks and always fill the most constrained cell, not the next one in reading order.",
    "time": "O(9^m) for m blanks in theory; propagation keeps real boards at a few thousand nodes",
    "space": "O(m) recursion depth plus 27 integers of state",
    "sections": [
        (
            "What it asks",
            """
Fill every `.` on a 9×9 grid so each row, column and 3×3 box holds `1`–`9`
exactly once. Mutate the board in place; LeetCode guarantees exactly one
solution.

Ask whether uniqueness is guaranteed. If it is, you may stop at the first
completion. If it is not, "solve" becomes "enumerate", the return type changes,
and the pruning below still applies but you can no longer short-circuit.

Also ask whether the input is guaranteed self-consistent. A board that already
violates a rule should fail fast rather than search 9⁶⁴ dead ends.
""",
        ),
        (
            "The insight",
            """
The naive shape — walk the blanks in reading order, try `1`–`9`, recurse — is
correct and will time out on anything adversarial. Two changes fix it, and both
are about **information**, not micro-optimisation.

**1. Candidate sets as bitmasks.** Re-scanning a row, a column and a box to
validate a digit costs 27 reads per attempt. Instead carry
`rows[r]`, `cols[c]`, `boxes[b]` as 9-bit integers of used digits. Then

```
candidates = 0x1FF & ~(rows[r] | cols[c] | boxes[b])
```

is one expression, and choose/un-choose are two XORs. Validation drops from
O(27) to O(1).

**2. Most-constrained-variable ordering (MRV).** Before each placement, scan the
remaining blanks and take the one with the *fewest* candidates. A cell with one
candidate is forced — you have propagated a constraint without writing a
propagation engine. A cell with zero candidates means this branch is already
dead, and you learn that now instead of 30 levels deeper.

Reading order commits to a cell that may have 8 candidates while a forced cell
sits untouched, which is exactly how a puzzle with 17 clues explodes.
""",
        ),
        (
            "What makes it fast enough",
            """
The MRV scan costs O(m) per node, so a node is O(m) rather than O(1) — and it
still wins by orders of magnitude, because it multiplies the branching factor
down. Inkala's 17-clue "world's hardest sudoku" is in the cases below: reading
order chews through it, MRV finishes in about 30 ms of CPython.

Three details that decide a real submission:

- **Undo everything.** The board character *and* all three masks. Restoring two
  of the three is the classic bug and it produces a board that looks plausible
  and is wrong.
- **Iterate the candidate mask, not `range(1, 10)`.** `bit = mask & -mask`
  isolates the lowest set bit and `bit.bit_length()` is the digit, so the loop
  runs once per *legal* digit.
- **`best_count == 0` is a fast fail**, and breaking the MRV scan the moment you
  see a cell with one candidate saves the rest of the scan.

Stop the recursion at the first completion. Returning `bool` up the stack rather
than a flag on the enclosing scope is what lets you do that cleanly.
""",
        ),
    ],
}

FULL = 0x1FF  # bits 0..8 set: every digit used


def solve_sudoku(board: list[list[str]]) -> bool:
    """Fill `board` in place. Returns whether a completion was found."""
    rows = [0] * 9
    cols = [0] * 9
    boxes = [0] * 9
    blanks: list[tuple[int, int]] = []

    for r in range(9):
        for c in range(9):
            char = board[r][c]
            if char == ".":
                blanks.append((r, c))
                continue
            bit = 1 << (int(char) - 1)
            if rows[r] & bit or cols[c] & bit or boxes[(r // 3) * 3 + c // 3] & bit:
                return False  # the givens already contradict each other
            rows[r] |= bit
            cols[c] |= bit
            boxes[(r // 3) * 3 + c // 3] |= bit

    def explore(cells: list[tuple[int, int]]) -> bool:
        if not cells:
            return True

        # Most-constrained variable: the blank with the fewest legal digits.
        best = 0
        best_mask = 0
        best_count = 10
        for i, (r, c) in enumerate(cells):
            mask = FULL & ~(rows[r] | cols[c] | boxes[(r // 3) * 3 + c // 3])
            count = mask.bit_count()
            if count < best_count:
                best, best_mask, best_count = i, mask, count
                if count <= 1:
                    break  # forced (or dead) — no better cell exists
        if best_count == 0:
            return False  # a blank with no candidate: this branch is dead

        r, c = cells[best]
        b = (r // 3) * 3 + c // 3
        rest = cells[:best] + cells[best + 1 :]

        mask = best_mask
        while mask:
            bit = mask & -mask  # lowest legal digit
            mask ^= bit
            rows[r] |= bit
            cols[c] |= bit
            boxes[b] |= bit
            board[r][c] = str(bit.bit_length())  # 1 << (d-1) has bit_length d

            if explore(rest):
                return True

            board[r][c] = "."  # un-choose: the character *and* all three masks
            rows[r] ^= bit
            cols[c] ^= bit
            boxes[b] ^= bit

        return False

    return explore(blanks)


CLASSIC = [
    "53..7....",
    "6..195...",
    ".98....6.",
    "8...6...3",
    "4..8.3..1",
    "7...2...6",
    ".6....28.",
    "...419..5",
    "....8..79",
]
CLASSIC_SOLVED = [
    "534678912",
    "672195348",
    "198342567",
    "859761423",
    "426853791",
    "713924856",
    "961537284",
    "287419635",
    "345286179",
]
# Inkala's 17-clue "world's hardest sudoku": reading order crawls, MRV does not.
HARDEST = [
    "8........",
    "..36.....",
    ".7..9.2..",
    ".5...7...",
    "....457..",
    "...1...3.",
    "..1....68",
    "..85...1.",
    ".9....4..",
]
HARDEST_SOLVED = [
    "812753649",
    "943682175",
    "675491283",
    "154237896",
    "369845721",
    "287169534",
    "521974368",
    "438526917",
    "796318452",
]

CASES = [
    ((CLASSIC,), CLASSIC_SOLVED),
    ((HARDEST,), HARDEST_SOLVED),
    # Already complete: zero blanks, so the answer is the input.
    ((CLASSIC_SOLVED,), CLASSIC_SOLVED),
    # Five blanks, each forced by propagation alone — no branching at all.
    (
        (
            [
                ".34678912",
                "672195348",
                "19834.567",
                "859761423",
                "4268.3791",
                "713924856",
                "9.1537284",
                "287419635",
                "34528617.",
            ],
        ),
        CLASSIC_SOLVED,
    ),
]


def solve(rows: list[str]) -> list[str]:
    """Rows as strings in, rows as strings out — `board` itself is never touched."""
    board = [list(row) for row in rows]
    solve_sudoku(board)
    return ["".join(row) for row in board]


def _is_complete(grid: list[str]) -> bool:
    digits = set("123456789")
    if any(set(row) != digits for row in grid):
        return False
    if any({row[c] for row in grid} != digits for c in range(9)):
        return False
    return all(
        {grid[br + i][bc + j] for i in range(3) for j in range(3)} == digits
        for br in (0, 3, 6)
        for bc in (0, 3, 6)
    )


def check() -> None:
    for args, expected in CASES:
        assert solve(*args) == expected

    # The givens must survive, and the result must actually be a valid grid.
    for puzzle in (CLASSIC, HARDEST):
        filled = solve(puzzle)
        assert _is_complete(filled)
        for r in range(9):
            for c in range(9):
                assert puzzle[r][c] in (".", filled[r][c])

    # No clues at all: any complete grid is correct, so verify rather than compare.
    assert _is_complete(solve(["." * 9] * 9))

    # A contradiction in the givens is detected before any search happens.
    contradictory = [list(row) for row in ["55.......", *["." * 9] * 8]]
    assert solve_sudoku(contradictory) is False
