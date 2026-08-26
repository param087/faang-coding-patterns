"""Design Excel Sum Formula — LeetCode 631."""

from __future__ import annotations

from collections import Counter

META = {
    "pattern": "ood",
    "symbol": "Excel",
    "insight": "Store the formula, not its result: a cell is either a literal or a multiset of references, and reads evaluate the DAG on demand.",
    "time": "O(1) to set, O(cells reachable) to read, O(area) to define a sum",
    "space": "O(cells set + references stored)",
    "sections": [
        (
            "What it asks",
            """
This one is **premium**, so the statement is not public — described here in my
own words.

A spreadsheet of `height` rows (1-based) and columns `"A"` upwards, every cell
starting at 0:

- `set(row, column, value)` — write a literal;
- `get(row, column)` — read the current value;
- `sum(row, column, refs)` — make the cell **a live formula** equal to the total
  of `refs`, each either a single cell like `"A1"` or a rectangle like
  `"A1:B2"`, and return that total now.

The word doing the work is *live*. A formula cell is not a number that was
computed once; when anything it references changes later, `get` must reflect it.

Ask three things. Does `set` on a formula cell destroy the formula? (Yes — a
literal replaces it, exactly like typing over a formula in a real spreadsheet.)
Can formulas reference other formulas? (Yes, and that is the interesting case.)
Can references form a cycle? (No, guaranteed — so the references form a DAG, and
you may skip cycle detection if you *say* you are skipping it.)
""",
        ),
        (
            "The insight",
            """
There are two workable architectures and the choice is the interview.

**Eager: push.** Keep reverse edges — for each cell, who depends on it — and on
every `set`, walk the dependents propagating the delta. Reads become O(1), which
is the right call for a spreadsheet UI where reads vastly outnumber writes. It
also costs you a second graph to maintain, delta arithmetic that has to respect
reference multiplicity, and a re-plumbing of the reverse edges every time a
`sum` is redefined. Plenty of ways to be subtly wrong under a clock.

**Lazy: pull.** A cell holds *either* a literal *or* a `Counter` of the cells it
references, and `get` evaluates recursively down the DAG. Writes are trivially
O(1) and, crucially, **cannot leave stale state** — there is no cached result to
invalidate. Redefining a formula is one dictionary assignment. This is the one
to write, and the argument to give for it is staleness, not speed.

Two details make the lazy version correct rather than nearly correct:

- **A `Counter`, not a set.** `sum(1, "C", ["A1", "A1"])` counts A1 twice, and a
  range that overlaps another range double-counts the intersection. Multiplicity
  is part of the semantics; a set silently under-counts.
- **A memo dict threaded through one evaluation.** A diamond — C references B
  twice, B references A — is exponential in the depth without it and linear in
  the DAG's edges with it. It must be per-`get`, not persistent, or you are back
  to cache invalidation.

Parsing is the boring half: a reference is one column letter followed by a
possibly multi-digit row, so `ref[0]` and `int(ref[1:])`. Storing cells as
`(row, column_index)` tuples rather than strings means a range expands with two
`range` loops and no string arithmetic.
""",
        ),
        (
            "Edge cases, and what gets probed",
            """
- **`set` must clear the formula, and `sum` must clear the literal.** Update one
  dictionary and forget the other and the cell has two identities; whichever the
  evaluator checks first wins, and the bug appears only after a cell has been
  both a formula and a literal.
- **Reversed ranges.** `"B2:A1"` is not in the constraints, but normalising with
  `min`/`max` on both axes costs one line and removes the question.
- **Unset cells read as 0**, which `dict.get(cell, 0)` gives for free — no
  pre-filled `height x width` grid, so a 26-column sheet with three used cells
  stores three cells.
- **A formula over a range that includes formula cells** is fine and is the case
  worth testing: define B1 from A1, then C1 from B1, then change A1 and read C1.
- **Cycles.** Guaranteed absent, and the lazy evaluator would recurse until the
  stack blew — so name the fix: mark cells grey/black during a DFS on `sum`,
  reject the definition if the new edges reach the target cell. One paragraph of
  code you do not have to write, but should offer.
- **Depth.** A 200-deep chain recurses 200 frames, comfortably inside Python's
  limit; a 10⁵-deep chain would need an explicit stack or an iterative
  post-order. Worth flagging as the scale limit of the recursive form.
""",
        ),
    ],
}

Cell = tuple[int, int]


class Excel:
    """Each cell is a literal or a multiset of references; reads pull, writes push nothing."""

    def __init__(self, height: int, width: str) -> None:
        self.height = height
        self.width = ord(width) - ord("A") + 1
        self.literal: dict[Cell, int] = {}
        self.formula: dict[Cell, Counter[Cell]] = {}

    @staticmethod
    def _cell(ref: str) -> Cell:
        return int(ref[1:]), ord(ref[0]) - ord("A")  # "B12" -> (12, 1)

    def _expand(self, refs: list[str]) -> Counter[Cell]:
        counts: Counter[Cell] = Counter()
        for ref in refs:
            if ":" not in ref:
                counts[self._cell(ref)] += 1
                continue
            start, end = ref.split(":")
            (row_a, col_a), (row_b, col_b) = self._cell(start), self._cell(end)
            for row in range(min(row_a, row_b), max(row_a, row_b) + 1):
                for col in range(min(col_a, col_b), max(col_a, col_b) + 1):
                    counts[(row, col)] += 1  # multiplicity matters: overlaps double-count
        return counts

    def _evaluate(self, cell: Cell, memo: dict[Cell, int]) -> int:
        if cell in memo:
            return memo[cell]
        refs = self.formula.get(cell)
        if refs is None:
            value = self.literal.get(cell, 0)  # unset cells read as 0
        else:
            value = sum(count * self._evaluate(ref, memo) for ref, count in refs.items())
        memo[cell] = value
        return value

    def set(self, row: int, column: str, value: int) -> None:
        cell = (row, ord(column) - ord("A"))
        self.formula.pop(cell, None)  # a literal destroys the formula
        self.literal[cell] = value

    def get(self, row: int, column: str) -> int:
        return self._evaluate((row, ord(column) - ord("A")), {})

    def sum(self, row: int, column: str, refs: list[str]) -> int:
        cell = (row, ord(column) - ord("A"))
        self.literal.pop(cell, None)  # and a formula destroys the literal
        self.formula[cell] = self._expand(refs)
        return self._evaluate(cell, {})


def check() -> None:
    sheet = Excel(3, "C")
    sheet.set(1, "A", 2)
    # A1 counted once on its own, then again inside the A1:B2 rectangle.
    assert sheet.sum(3, "C", ["A1", "A1:B2"]) == 4
    sheet.set(2, "B", 2)
    assert sheet.get(3, "C") == 6  # the formula is live, not a snapshot

    # Formulas over formulas, and a change at the bottom of the chain.
    chain = Excel(4, "D")
    chain.set(1, "A", 1)
    assert chain.sum(1, "B", ["A1"]) == 1
    assert chain.sum(1, "C", ["B1", "B1"]) == 2  # duplicate reference counts twice
    assert chain.sum(1, "D", ["C1", "B1"]) == 3
    chain.set(1, "A", 5)
    assert chain.get(1, "B") == 5
    assert chain.get(1, "C") == 10
    assert chain.get(1, "D") == 15

    # set() over a formula cell severs it: D1 stops tracking A1 for good.
    chain.set(1, "D", 100)
    assert chain.get(1, "D") == 100
    chain.set(1, "A", 0)
    assert chain.get(1, "D") == 100
    assert chain.get(1, "C") == 0

    # And sum() over a literal cell severs the literal.
    chain.set(2, "A", 7)
    assert chain.get(2, "A") == 7
    assert chain.sum(2, "A", ["A1"]) == 0
    chain.set(1, "A", 9)
    assert chain.get(2, "A") == 9

    # Untouched cells are 0, and a range over nothing sums to 0.
    blank = Excel(2, "B")
    assert blank.get(2, "B") == 0
    assert blank.sum(1, "A", ["A2:B2"]) == 0
    blank.set(2, "B", 3)
    assert blank.get(1, "A") == 3

    # Overlapping ranges double-count the intersection.
    overlap = Excel(2, "B")
    overlap.set(1, "A", 1)
    overlap.set(1, "B", 10)
    overlap.set(2, "A", 100)
    overlap.set(2, "B", 1000)
    assert overlap.sum(2, "B", ["A1:A2", "A1:B1"]) == 1 + 100 + 1 + 10
    # B2 is now a formula, so its old literal 1000 no longer contributes anywhere.
    assert overlap.get(2, "B") == 112
