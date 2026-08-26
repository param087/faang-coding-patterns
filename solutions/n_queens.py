"""N-Queens — LeetCode 51."""

from __future__ import annotations

META = {
    "pattern": "backtracking",
    "insight": "One queen per row turns placement into a permutation of columns, and r+c / r-c turn the diagonal test into two set lookups.",
    "time": "O(n!) nodes in the pruned tree, O(n² · solutions) to render the boards",
    "space": "O(n) for the recursion and the three conflict sets, excluding the output",
    "sections": [
        (
            "What it asks",
            """
Place `n` queens on an `n × n` board so that no two attack each other — no
shared row, column, or diagonal — and return **every** distinct arrangement,
each as `n` strings of `.` and `Q`.

Confirm the output shape early: **all** boards rendered as strings, not the
count (that is N-Queens II) and not one board (that is the easier greedy
question). Rendering is a real fraction of the runtime at n = 9 and it is
worth knowing whether you have to pay it.

Also confirm that reflections and rotations count as distinct. They do here —
n = 4 has two solutions, and they are mirror images of each other.
""",
        ),
        (
            "Brute force, and why it fails",
            """
"Choose n squares out of n²" for n = 8 is C(64, 8) = **4 426 165 368**
placements, each needing a validity scan. That is the answer you must not
write, but it is the answer worth stating, because the first reduction falls
straight out of it.

Two queens in one row attack each other, so every solution has **exactly one
queen per row**. Now a candidate board is just a choice of column for each row:
n^n = 8⁸ = **16 777 216**, a 264× cut for one observation.

Columns must also be distinct, so a candidate is a **permutation** of columns:
8! = **40 320**. And with diagonal conflicts checked incrementally as you
descend — rejecting a partial board before extending it — the search actually
visits about **2057 nodes** to find the 92 solutions for n = 8.

4.4 billion → 2057. That progression, said out loud, is most of the interview.
""",
        ),
        (
            "The insight",
            """
Recurse on **rows**. At row `r`, try each column `c` and ask a single question:
does placing a queen here conflict with any queen already placed in rows
`0..r-1`?

Rows are handled by construction. Columns need a set. Diagonals need the trick
that makes this problem quick to write:

- Every square on a `↘` diagonal has the **same `r - c`**.
- Every square on a `↙` diagonal has the **same `r + c`**.

So three sets — `cols`, `diag`, `anti` — and the conflict test is three O(1)
lookups. Choose, recurse, un-choose; when `r == n`, render the board.

The `r - c` values run from `-(n-1)` to `n-1`, which is fine for a Python set
but needs the `+ (n - 1)` offset if you are backing it with an array — and
becomes the shift you need anyway if you go bitmask later.
""",
        ),
        (
            "The pruning that actually matters",
            """
The detail that decides this problem is **where** the conflict test lives.

Testing at the leaf — build a full permutation, then scan for diagonal
conflicts — is still 8! = 40 320 boards with an O(n²) check on each. Testing
**before descending** prunes at row 2 or 3 for most branches, and that is the
40 320 → 2057 step. The rule generalises: in backtracking, a check that runs
one level too late costs you a whole factor of the branching factor.

Track the sets incrementally too. Re-deriving conflicts by scanning `placed`
on every candidate is O(n) per test and turns an O(1) inner loop into O(n) — it
still passes, but it is the difference between "I know why this is fast" and
"it worked". Add on the way down, remove on the way back up, in the same three
lines as the queen itself.
""",
        ),
        (
            "Dry run — n = 4",
            """
- Row 0, column 0. Blocks column 0, diagonal `r-c = 0`, anti-diagonal
  `r+c = 0`.
- Row 1: column 0 is taken, and column 1 has `r-c = 0` so it sits on the
  blocked diagonal. First legal square is column 2.
- Row 2: column 0 is taken, column 1 sits on anti-diagonal `2+1=3` with (1,2),
  column 2 is taken, column 3 sits on diagonal `2-3=-1` with (1,2). **Dead
  end** — back up.
- Row 1 moves to column 3. Row 2 then admits only column 1. Row 3 has nothing
  legal. Back up again, all the way past row 0.
- Row 0, column 1 → row 1 column 3 → row 2 column 0 → row 3 column 2.
  **Solution**: `.Q..`, `...Q`, `Q...`, `..Q.`

The second solution is that board mirrored. Notice how much of the tree died at
row 2: that is the whole algorithm working.
""",
        ),
        (
            "The complexity question",
            """
Say **O(n!)** and then immediately say why it is loose: n! counts column
permutations, and the diagonal pruning removes almost all of them, but there is
no closed form for the number of solutions — the sequence 1, 0, 0, 2, 10, 4,
40, 92, 352 (OEIS A000170) has no known formula and is only computed by search.

So the honest statement is "O(n!) as an upper bound on nodes, with the true
count far smaller and not expressible in closed form". Add that rendering costs
O(n²) per solution, which at n = 9 (352 solutions) is a non-trivial share of the
work.

If the interviewer pushes on constants rather than asymptotics, that is the cue
for the bitmask version below.
""",
        ),
        (
            "Follow-ups",
            """
- **N-Queens II — count only.** Same search, drop `path` and the rendering, and
  return an integer. Roughly 2–3× faster purely from not building strings.
- **Bitmasks.** Represent `cols`, `diag`, `anti` as integers and compute the
  legal squares for a row in one expression:
  `free = ~(cols | diag | anti) & ((1 << n) - 1)`, then iterate with
  `bit = free & -free; free -= bit`. The recursive call shifts:
  `solve(cols | bit, (diag | bit) << 1, (anti | bit) >> 1)`. Same asymptotics,
  usually 5–10× faster, and it is the version competitive programmers write.
- **Sudoku Solver (37)** is the same shape with three constraint families —
  row, column, box — and the same "check before descending" rule. The
  strong-ordering heuristic (fill the cell with the fewest candidates first)
  matters far more there than it does here.
- **"Just find one solution."** Return early on the first hit. There are also
  explicit constructions for a single solution for every n ≥ 4, which is worth
  knowing exists but is not what an interview is asking for.
""",
        ),
    ],
}


def solve_n_queens(n: int) -> list[list[str]]:
    boards: list[list[str]] = []
    queen_column: list[int] = []  # queen_column[row] = column
    cols: set[int] = set()
    diag: set[int] = set()  # r - c, constant along a "\" diagonal
    anti: set[int] = set()  # r + c, constant along a "/" diagonal

    def explore(row: int) -> None:
        if row == n:
            boards.append(["." * c + "Q" + "." * (n - c - 1) for c in queen_column])
            return
        for col in range(n):
            if col in cols or (row - col) in diag or (row + col) in anti:
                continue  # rejected before descending — this is the pruning
            cols.add(col)
            diag.add(row - col)
            anti.add(row + col)
            queen_column.append(col)

            explore(row + 1)

            queen_column.pop()
            anti.discard(row + col)
            diag.discard(row - col)
            cols.discard(col)

    explore(0)
    return boards


def total_n_queens(n: int) -> int:
    """N-Queens II, bitmask form: count only, no board rendering."""
    full = (1 << n) - 1

    def explore(cols: int, diag: int, anti: int) -> int:
        if cols == full:
            return 1
        free = ~(cols | diag | anti) & full
        found = 0
        while free:
            bit = free & -free
            free -= bit
            found += explore(cols | bit, (diag | bit) << 1, (anti | bit) >> 1)
        return found

    return explore(0, 0, 0)


CASES = [
    ((4,), [[".Q..", "...Q", "Q...", "..Q."], ["..Q.", "Q...", "...Q", ".Q.."]]),
    ((1,), [["Q"]]),
    ((2,), []),  # the smallest impossible board
    ((3,), []),
    ((0,), [[]]),  # vacuously one arrangement: the empty board
]


def solve(n: int) -> list[list[str]]:
    return solve_n_queens(n)


def _is_valid(board: list[str]) -> bool:
    n = len(board)
    if any(row.count("Q") != 1 or len(row) != n for row in board):
        return False
    columns = [row.index("Q") for row in board]
    if len(set(columns)) != n:
        return False
    if len({r - c for r, c in enumerate(columns)}) != n:
        return False
    return len({r + c for r, c in enumerate(columns)}) == n


def check() -> None:
    for args, expected in CASES:
        assert solve_n_queens(*args) == expected

    # A000170: solution counts for n = 0..9. No closed form exists.
    counts = [1, 1, 0, 0, 2, 10, 4, 40, 92, 352]
    for n, expected_count in enumerate(counts):
        boards = solve_n_queens(n)
        assert len(boards) == expected_count, (n, len(boards))
        assert all(_is_valid(board) for board in boards)
        # The bitmask counter must agree with the board-building search.
        assert total_n_queens(n) == expected_count
