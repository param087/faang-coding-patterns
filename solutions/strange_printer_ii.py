"""Strange Printer II — LeetCode 1591."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "advanced-graphs",
    "insight": "Each colour's bounding box forces every colour inside it to be printed later; printable iff those forcings have no cycle.",
    "time": "O(C·m·n) with C ≤ 60 colours",
    "space": "O(C²)",
    "sections": [
        (
            "What it asks",
            """
The printer prints an axis-aligned solid rectangle of one colour per operation,
each colour may be used **at most once**, and later prints paint over earlier
ones. Given the finished grid, decide whether some sequence of prints produces
it. Colours are `1..60`, the grid is at most `60 × 60`.

Two clarifications that change the problem, so ask them: does *every* cell have
to be covered (yes — there is no blank colour, so the first print must be big
enough), and is one print per colour a hard cap (yes, and that cap is the whole
difficulty — with unlimited prints per colour every grid is printable, paint
cell by cell).
""",
        ),
        (
            "The insight",
            """
Forget the pixels; the only real unknown is the **order** in which the ≤ 60
colours were printed. Once you have an order, the rectangles are forced.

Because colour `c` is printed exactly once as a solid rectangle, and every cell
still showing `c` at the end had to be inside that rectangle, the rectangle
must contain the **bounding box** of `c`'s visible cells. Printing anything
larger only makes life harder, so take the bounding box itself.

Now the constraint falls out. Look inside `c`'s bounding box. Every cell there
that ends up showing some other colour `d` was painted `c` first and then
overwritten — so **`d` must be printed after `c`**. That is a directed edge
`c → d`.

Collect those edges for all colours and you have a precedence graph on ≤ 60
nodes. A valid print order is exactly a topological order of it. So:

> **printable ⟺ the precedence graph is acyclic.**

Run Kahn's algorithm and compare the number of colours emitted against the
number of distinct colours present. That is the entire solution — the graph is
tiny, so the cost is dominated by scanning each colour's box, O(C·m·n) ≈
60 · 3600 = 2.2·10⁵ operations at the limits.

The reason this is a Hard: nothing in the statement says "graph". The jump from
"which rectangles?" to "which order?" to "is there a cycle?" is the question.
""",
        ),
        (
            "Two ways to build the wrong graph",
            """
**Scanning only the cells of colour `c`.** The whole point is the cells inside
`c`'s box that are *not* `c` — those are the overwrites. Iterate the full
rectangle `[top..bottom] × [left..right]`, not `c`'s pixel list, or you build
an edgeless graph and return `True` for everything.

**Deriving edges from adjacency.** "Colour `d` touches colour `c`, so one
covered the other" is not sound in either direction. Containment in a bounding
box is the only relation that carries information; two colours can be adjacent
everywhere and independent.

Two details that are easy to lose:

- Skip the self-edge when the cell inside `c`'s box is `c` itself, otherwise
  every colour has in-degree ≥ 1 and Kahn's starts with an empty queue.
- Key the graph on colours **present in the grid**, not on `1..60`. Absent
  colours are never printed and adding them as isolated nodes changes the
  count you compare against.

The case that separates a correct implementation from a plausible one is a lone
cell of an early colour surrounded by a later one — `[[1,2,1],[2,1,2],[1,2,1]]`.
Both bounding boxes are the whole grid, each contains the other, `1 ⇄ 2`, so
the answer is `False`. Any solution that only looks at rectangle *sizes* or at
nesting depth says `True`.
""",
        ),
    ],
}


def is_printable(target_grid: list[list[int]]) -> bool:
    rows = len(target_grid)
    cols = len(target_grid[0]) if rows else 0

    # Smallest rectangle that could have been printed for each colour.
    box: dict[int, tuple[int, int, int, int]] = {}
    for r in range(rows):
        for c in range(cols):
            colour = target_grid[r][c]
            if colour in box:
                top, bottom, left, right = box[colour]
                box[colour] = (min(top, r), max(bottom, r), min(left, c), max(right, c))
            else:
                box[colour] = (r, r, c, c)

    # colour -> colours that must be printed after it.
    after: dict[int, set[int]] = {colour: set() for colour in box}
    for colour, (top, bottom, left, right) in box.items():
        for r in range(top, bottom + 1):
            for c in range(left, right + 1):
                other = target_grid[r][c]
                if other != colour:  # skip the self-edge
                    after[colour].add(other)

    # Kahn: printable iff this precedence graph has a topological order.
    indegree = dict.fromkeys(box, 0)
    for successors in after.values():
        for other in successors:
            indegree[other] += 1

    queue = deque(colour for colour, degree in indegree.items() if degree == 0)
    printed = 0
    while queue:
        colour = queue.popleft()
        printed += 1
        for other in after[colour]:
            indegree[other] -= 1
            if indegree[other] == 0:
                queue.append(other)

    return printed == len(box)


CASES = [
    (([[1, 1, 1, 1], [1, 2, 2, 1], [1, 2, 2, 1], [1, 1, 1, 1]],), True),
    (([[1, 1, 1, 1], [1, 1, 3, 3], [1, 1, 3, 4], [5, 5, 1, 4]],), True),
    # Mutual containment: 1's box holds a 2 and 2's box holds a 1.
    (([[1, 2, 1], [2, 1, 2], [1, 2, 1]],), False),
    # The 3s force a full row-1 rectangle, which would bury the visible 1 at (1, 1).
    (([[1, 1, 1], [3, 1, 3]],), False),
    # Three-deep chain 1 -> 2 -> 3, acyclic.
    (
        ([[1, 1, 1, 1], [1, 2, 2, 2], [1, 2, 3, 2], [1, 2, 2, 2]],),
        True,
    ),
    # Same grid with a stray 1 inside 2's box, which closes the cycle 1 -> 2 -> 1.
    (
        ([[1, 1, 1, 1], [1, 2, 2, 2], [1, 2, 1, 2], [1, 2, 2, 2]],),
        False,
    ),
    (([[7, 7], [7, 7]],), True),
    (([[1]],), True),
]


def solve(target_grid: list[list[int]]) -> bool:
    return is_printable([row[:] for row in target_grid])
