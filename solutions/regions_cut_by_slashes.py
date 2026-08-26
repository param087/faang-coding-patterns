"""Regions Cut By Slashes — LeetCode 959."""

from __future__ import annotations

META = {
    "pattern": "union-find",
    "insight": "A slash cuts a cell in two, so a cell cannot be one node — split each cell into four triangles and let the character say which touch.",
    "time": "O(n² · α(n²))",
    "space": "O(n²)",
    "sections": [
        (
            "What it asks",
            """
An `n × n` grid where each cell holds a forward slash, a backslash or a space.
The slashes are drawn corner to corner. Count the connected regions of the
resulting picture.

Ask whether regions touching only at a **point** count as one (they do not —
two pieces meeting at a shared corner are separate), and confirm `n ≤ 30`,
which tells you a `4n²` = 3,600-node structure is free.
""",
        ),
        (
            "The insight",
            """
The instinct is "flood fill, one node per cell". That is wrong on arrival: a
cell containing a slash belongs to **two different regions**, so a cell cannot
be a node.

Subdivide. Each cell becomes four triangles, numbered clockwise from the top —
0 north, 1 east, 2 south, 3 west. Now every piece of the picture is a whole
node, and the character only decides which triangles *inside* a cell are
joined:

- space — join all four;
- forward slash — the line runs bottom-left to top-right, so it leaves
  {0, 3} on one side and {1, 2} on the other;
- backslash — top-left to bottom-right, so it joins {0, 1} and {2, 3}.

Between cells there is never a barrier: join this cell's 1 (east) to the right
neighbour's 3 (west), and this cell's 2 (south) to the lower neighbour's 0
(north). Two joins per cell, not four — the reverse pairs happen when the
neighbour takes its turn.

The answer is the number of distinct roots among the `4n²` triangles, i.e.
`4n²` minus the number of unions that actually merged something.

The alternative is upscaling each cell to a 3×3 block of pixels, marking the
diagonal as wall, and flood-filling — same complexity, and 3 is the smallest
factor that keeps a diagonal connected. Mention it, then write the DSU: it is
shorter and has no magic constant.
""",
        ),
        (
            "Getting the orientation right",
            """
Everything hinges on which triangles each character joins, and the two
characters are easy to swap under pressure. Anchor it on the picture rather
than on memory: a forward slash runs from the **bottom-left corner to the
top-right corner**, and the top-right of the cell is triangles 0 and 1 while
the bottom-left is 2 and 3 — so it joins 0-3 and 1-2, the pairs the line
leaves on the same side.

Two more things that bite:

- the cross-cell joins must happen for **every** cell, including those holding
  a slash. The barrier is inside a cell, never on its boundary; skipping the
  neighbour joins for non-space cells is the common bug.
- rows arrive as strings, so `grid[r][c]` is a one-character string — compare
  against `"/"` and `"\\"` (the latter is a single backslash written as a
  Python escape), not against multi-character literals.

Sanity check with the Python literal `["/\\", "\\/"]`: the four half-diagonals
form a diamond in the middle, giving the diamond plus four corner pieces —
**5** regions. Swap the two characters to `["\\/", "/\\"]` and the lines form a
full X across the square: **4** regions. Code that returns the same number for
both has the orientation wrong, and no other test will tell you.
""",
        ),
    ],
}


class UnionFind:
    def __init__(self, n: int) -> None:
        self.parent = list(range(n))
        self.rank = [0] * n
        self.count = n

    def find(self, x: int) -> int:
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:  # path compression
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a: int, b: int) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        self.count -= 1
        return True


def regions_by_slashes(grid: list[str]) -> int:
    n = len(grid)
    dsu = UnionFind(4 * n * n)

    def node(row: int, col: int, triangle: int) -> int:
        return 4 * (row * n + col) + triangle  # 0 N, 1 E, 2 S, 3 W

    for row in range(n):
        for col in range(n):
            char = grid[row][col]

            if char == "/":  # bottom-left to top-right
                dsu.union(node(row, col, 0), node(row, col, 3))
                dsu.union(node(row, col, 1), node(row, col, 2))
            elif char == "\\":  # top-left to bottom-right
                dsu.union(node(row, col, 0), node(row, col, 1))
                dsu.union(node(row, col, 2), node(row, col, 3))
            else:  # blank: the whole cell is one piece
                dsu.union(node(row, col, 0), node(row, col, 1))
                dsu.union(node(row, col, 1), node(row, col, 2))
                dsu.union(node(row, col, 2), node(row, col, 3))

            # Cell boundaries are never barriers, whatever the cell holds.
            if col + 1 < n:
                dsu.union(node(row, col, 1), node(row, col + 1, 3))
            if row + 1 < n:
                dsu.union(node(row, col, 2), node(row + 1, col, 0))

    return dsu.count


CASES = [
    (([" /", "/ "],), 2),
    (([" /", "  "],), 1),
    ((["/\\", "\\/"],), 5),  # a diamond plus four corner pieces
    ((["\\/", "/\\"],), 4),  # same characters swapped: a full X
    ((["/"],), 2),
    ((["\\"],), 2),
    (([" "],), 1),
    ((["  ", "  "],), 1),
    ((["//", "/ "],), 3),
]


def solve(grid: list[str]) -> int:
    return regions_by_slashes(grid)
