"""Pacific Atlantic Water Flow — LeetCode 417."""

from __future__ import annotations

META = {
    "pattern": "graph-traversal",
    "insight": "Do not simulate rain from every cell — start at each ocean and walk uphill, then intersect the two reachable sets.",
    "time": "O(rows · cols)",
    "space": "O(rows · cols)",
    "sections": [
        (
            "What it asks",
            """
Water flows from a cell to an orthogonal neighbour of **equal or lower**
height. The Pacific touches the top and left edges, the Atlantic the bottom and
right. Return every cell from which water reaches both.

Ask: does equal height flow (yes — that is what makes plateaus reach both
oceans); does the output order matter (no); can the grid be a single row (yes,
and then every cell touches both oceans).
""",
        ),
        (
            "The insight",
            """
The obvious approach is a traversal from each cell asking "can I get out to
both oceans", which is O((rows·cols)²) — on the 200×200 grid the constraints
allow, 40,000 cells × 40,000 cells is 1.6 × 10⁹ steps, and memoising it across
starts is fiddly because reachability is direction-dependent.

Reverse the edges instead. "Water flows downhill from A to B" is the same
statement as "from B you can climb to A". So start at the ocean, walk to
neighbours that are **≥** the current height, and every cell you reach is a
cell that drains into that ocean. Two traversals over the whole grid, one per
ocean, then set-intersect.

Two traversals — not two per border cell. Seed the stack with the entire border
at once; a multi-source traversal visits each cell once no matter how many
sources could have reached it.
""",
        ),
        (
            "Why the comparison flips",
            """
Downhill simulation uses `heights[next] <= heights[current]`. The reversed
walk uses `heights[next] >= heights[current]`. Writing the forward comparison
while traversing backwards is the single most common way to fail this problem,
and it fails quietly: you get a plausible-looking, wrong set of cells.

Sanity check yourself on a grid that strictly descends toward the
bottom-right. Every cell drains to the Atlantic, so the Atlantic set is the
whole grid; only the top-left corner and its plateau reach the Pacific. If your
Pacific set comes back as the whole grid, your comparison is inverted.

`>=` and not `>` also matters: a flat plateau spanning the grid must reach both
oceans, and `>` would strand it.
""",
        ),
    ],
}

DIRECTIONS = ((0, 1), (1, 0), (0, -1), (-1, 0))


def pacific_atlantic(heights: list[list[int]]) -> list[list[int]]:
    if not heights or not heights[0]:
        return []

    rows, cols = len(heights), len(heights[0])

    def uphill_from(sources: set[tuple[int, int]]) -> set[tuple[int, int]]:
        seen = set(sources)
        stack = list(sources)
        while stack:
            r, c = stack.pop()
            for dr, dc in DIRECTIONS:
                nr, nc = r + dr, c + dc
                if (
                    0 <= nr < rows
                    and 0 <= nc < cols
                    and (nr, nc) not in seen
                    and heights[nr][nc] >= heights[r][c]  # climbing, not falling
                ):
                    seen.add((nr, nc))
                    stack.append((nr, nc))
        return seen

    pacific = uphill_from({(0, c) for c in range(cols)} | {(r, 0) for r in range(rows)})
    atlantic = uphill_from(
        {(rows - 1, c) for c in range(cols)} | {(r, cols - 1) for r in range(rows)}
    )

    return sorted([r, c] for r, c in pacific & atlantic)


CASES = [
    (
        (
            [
                [1, 2, 2, 3, 5],
                [3, 2, 3, 4, 4],
                [2, 4, 5, 3, 1],
                [6, 7, 1, 4, 5],
                [5, 1, 1, 2, 4],
            ],
        ),
        [[0, 4], [1, 3], [1, 4], [2, 2], [3, 0], [3, 1], [4, 0]],
    ),
    (([[3, 2], [2, 1]],), [[0, 0], [0, 1], [1, 0]]),  # descends: Atlantic gets all
    (([[1, 1], [1, 1]],), [[0, 0], [0, 1], [1, 0], [1, 1]]),  # plateau needs >=, not >
    (([[1, 2, 3]],), [[0, 0], [0, 1], [0, 2]]),  # one row touches both oceans
    (([[1]],), [[0, 0]]),
    (([],), []),
]


def solve(heights: list[list[int]]) -> list[list[int]]:
    return pacific_atlantic(heights)
