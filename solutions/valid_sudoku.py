"""Valid Sudoku — LeetCode 36."""

from __future__ import annotations

META = {
    "pattern": "arrays-hashing",
    "insight": "Validity is nine row sets, nine column sets and nine box sets; box = (r // 3) * 3 + c // 3 fills all three in one pass.",
    "time": "O(1) — 81 cells",
    "space": "O(1) — 27 sets of at most 9 digits",
    "sections": [
        (
            "What it asks",
            """
Decide whether a partially filled 9×9 board **breaks a rule right now**: no
digit twice in a row, a column, or a 3×3 box. Empty cells are `"."`.

The clarifying question that matters, and the one candidates skip: *does this
ask whether the board is solvable?* **No.** A board can be perfectly valid by
this definition and still have no completion. Confirm it, because the wrong
reading sends you into a backtracking solver and burns the interview.

Second question: are the digits characters or ints? LeetCode gives characters,
so `"5"` not `5`, and no conversion is needed at all.
""",
        ),
        (
            "The insight",
            """
Three independent constraints, each of which is just "have I seen this digit in
this group before?" That is a set, and there are 27 groups: 9 rows, 9 columns,
9 boxes.

The only piece of arithmetic in the problem is naming the box a cell belongs
to:

```
box = (r // 3) * 3 + c // 3
```

`r // 3` picks the band, `c // 3` picks the stack, and the `* 3` lays the grid
out row-major into `0..8`. Get that line right and one pass over 81 cells fills
and checks all three families simultaneously — no second traversal, no nested
`for br in range(3): for bc in range(3):` block.

Because the board is fixed at 9×9, the honest complexity is **O(1)**. Say that,
then give the general form for an `n²×n²` board: O(n⁴) cells, O(n⁴) space.
""",
        ),
        (
            "Where it goes wrong",
            """
- **Checking rows and columns only.** The commonest bug, and it passes the
  sample. Two identical digits at `(0, 0)` and `(1, 1)` share no row and no
  column but do share a box. That exact board is in the cases below.
- **One global set instead of 27.** Then every digit collides with itself the
  second time it appears anywhere, and a legal board with `1` at `(0, 0)` and
  `1` at `(4, 4)` is rejected. Also in the cases below.
- **Forgetting `"."`.** Nine dots in a row is not a conflict. Skip them before
  any set operation.
- **`(r // 3) + (c // 3) * 3`** — the transposed variant. It is also a valid
  bijection onto `0..8`, so it happens to work; `(r // 3) + (c // 3)` is not,
  and quietly merges boxes along the anti-diagonal.
""",
        ),
    ],
}


def is_valid_sudoku(board: list[list[str]]) -> bool:
    rows: list[set[str]] = [set() for _ in range(9)]
    cols: list[set[str]] = [set() for _ in range(9)]
    boxes: list[set[str]] = [set() for _ in range(9)]

    for r in range(9):
        for c in range(9):
            digit = board[r][c]
            if digit == ".":
                continue

            b = (r // 3) * 3 + c // 3  # band * 3 + stack, row-major into 0..8
            if digit in rows[r] or digit in cols[c] or digit in boxes[b]:
                return False

            rows[r].add(digit)
            cols[c].add(digit)
            boxes[b].add(digit)

    return True


def _board(rows: list[str]) -> list[list[str]]:
    return [list(row) for row in rows]


def _sparse(cells: dict[tuple[int, int], str]) -> list[list[str]]:
    grid = [["." for _ in range(9)] for _ in range(9)]
    for (r, c), digit in cells.items():
        grid[r][c] = digit
    return grid


VALID = _board(
    [
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
)

# Same board with the leading 5 changed to an 8: column 0 now holds two 8s.
COLUMN_CLASH = _board(
    [
        "83..7....",
        "6..195...",
        ".98....6.",
        "8...6...3",
        "4..8.3..1",
        "7...2...6",
        ".6....28.",
        "...419..5",
        "....8..79",
    ]
)

CASES = [
    ((VALID,), True),
    ((COLUMN_CLASH,), False),
    ((_sparse({}),), True),
    ((_sparse({(0, 0): "1", (1, 1): "1"}),), False),  # box only: no shared row or column
    ((_sparse({(0, 0): "1", (0, 5): "1"}),), False),  # row only: different boxes
    ((_sparse({(0, 0): "1", (5, 0): "1"}),), False),  # column only: different boxes
    ((_sparse({(0, 0): "1", (4, 4): "1", (8, 8): "1"}),), True),  # a global set rejects this
]


def solve(board: list[list[str]]) -> bool:
    return is_valid_sudoku([row[:] for row in board])
