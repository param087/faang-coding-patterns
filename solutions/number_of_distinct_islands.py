"""Number of Distinct Islands — LeetCode 694 (Premium)."""

from __future__ import annotations

META = {
    "pattern": "graph-traversal",
    "insight": "Translate every island to the origin during the flood fill, so identical shapes hash to identical keys.",
    "time": "O(rows · cols)",
    "space": "O(rows · cols)",
    "sections": [
        (
            "What it asks",
            """
LeetCode 694 is premium, so the statement is not public — the task in my own
words: a binary grid, `1` is land and `0` is water, islands are
four-directionally connected. Count how many **distinct shapes** appear, where
two islands are the same shape if one can be **translated** onto the other.
No rotation, no reflection.

Ask this before writing anything: *are rotations and reflections the same
shape?* Here they are not — that is 695's sibling, LeetCode 711, and it is a
genuinely harder problem (eight transforms, canonicalise by min). If the
interviewer says "rotations count too", you need a different plan.
""",
        ),
        (
            "The insight",
            """
The count of islands is the easy half — it is 200 with a counter. The whole
question is **how you key a shape**.

Absolute coordinates are useless: two identical islands in different corners
of the grid produce completely different cell sets. Subtract the anchor. Fix
the first cell the flood fill touches as `(r0, c0)` and record every cell as
`(r - r0, c - c0)`. Translation-invariance falls out for free, and the sorted
tuple of relative offsets is a hashable canonical form.

Cell **count** is not a key. A 1×3 bar and an L-tromino both have three cells.
Neither is a bounding box: an L and its mirror share a 2×2 box.
""",
        ),
        (
            "The path-signature variant and its trap",
            """
The other common encoding records the DFS **move string** — `"RDLU"` — instead
of coordinates. It is smaller and faster, and it is wrong unless you also emit
a marker on the way back up:

```
1 1        1 1
1 0        0 1
```

Left island: from the top-left, go right, backtrack, go down. Right island: go
right, then down. Both emit `"RD"` without a backtrack token, so a naive path
signature merges two genuinely different shapes. Appending a sentinel (`"b"`)
after each recursive call fixes it, because the sentinel records the tree
structure of the walk, not just its edges.

Relative coordinates dodge the whole argument, which is why they are the safer
thing to write with an interviewer watching. Mention that you know the path
trick; write the one you can prove.

Other edge cases: an empty grid or an all-water grid is 0, and duplicate
shapes anywhere in the grid must collapse to one entry — that is what the set
is for.
""",
        ),
    ],
}


def num_distinct_islands(grid: list[list[int]]) -> int:
    if not grid or not grid[0]:
        return 0

    rows, cols = len(grid), len(grid[0])
    shapes: set[tuple[tuple[int, int], ...]] = set()

    for r0 in range(rows):
        for c0 in range(cols):
            if grid[r0][c0] != 1:
                continue

            cells: list[tuple[int, int]] = []
            stack = [(r0, c0)]
            grid[r0][c0] = 0  # mark on push, never twice in the stack

            while stack:
                r, c = stack.pop()
                cells.append((r - r0, c - c0))  # anchored at the first cell
                for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                        grid[nr][nc] = 0
                        stack.append((nr, nc))

            shapes.add(tuple(sorted(cells)))  # sorted, so DFS order cannot leak in

    return len(shapes)


CASES = [
    # Same shape twice, in different corners -> 1.
    (([[1, 1, 0, 0, 0], [1, 1, 0, 0, 0], [0, 0, 0, 1, 1], [0, 0, 0, 1, 1]],), 1),
    (([[1, 1, 0, 1, 1], [1, 0, 0, 0, 1], [0, 0, 0, 0, 0], [1, 1, 0, 1, 1]],), 3),
    # The path-signature trap: both islands emit "RD" without a backtrack marker.
    (([[1, 1, 0, 1, 1], [1, 0, 0, 0, 1]],), 2),
    # Equal cell counts, different shapes -> a size-based key would say 1.
    (([[1, 1, 0], [0, 0, 0], [1, 0, 0], [1, 0, 0]],), 2),
    (([[1]],), 1),
    (([[0, 0], [0, 0]],), 0),
    (([],), 0),
]


def solve(grid: list[list[int]]) -> int:
    return num_distinct_islands([row[:] for row in grid])
