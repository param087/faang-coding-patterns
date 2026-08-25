"""Union-Find (disjoint set union).

Reach for it when connectivity **grows over time**. DFS answers "are these
connected" for a fixed graph; DSU answers it while edges are still arriving,
and answers it in near-constant time.

Both optimisations matter. Path compression alone is O(log n) amortised; with
union by rank it becomes O(alpha(n)), which is under 5 for any n you will meet.
"""

from __future__ import annotations


class UnionFind:
    """DSU with path compression and union by rank."""

    def __init__(self, n: int) -> None:
        self.parent = list(range(n))
        self.rank = [0] * n
        self.components = n

    def find(self, x: int) -> int:
        """Representative of x's set, flattening the path on the way back."""
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        # Second pass points everything on the path straight at the root.
        while self.parent[x] != root:
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a: int, b: int) -> bool:
        """Merge two sets. False if they were already joined.

        That boolean is the useful part: it is exactly "this edge closes a
        cycle", which is what Redundant Connection and Kruskal both need.
        """
        root_a, root_b = self.find(a), self.find(b)
        if root_a == root_b:
            return False

        # Hang the shorter tree off the taller one to keep depth down.
        if self.rank[root_a] < self.rank[root_b]:
            root_a, root_b = root_b, root_a
        self.parent[root_b] = root_a
        if self.rank[root_a] == self.rank[root_b]:
            self.rank[root_a] += 1

        self.components -= 1
        return True

    def connected(self, a: int, b: int) -> bool:
        return self.find(a) == self.find(b)


def count_components(n: int, edges: list[tuple[int, int]]) -> int:
    """Number of connected components after applying every edge."""
    dsu = UnionFind(n)
    for a, b in edges:
        dsu.union(a, b)
    return dsu.components


def find_redundant_connection(edges: list[list[int]]) -> list[int]:
    """The edge that turns a tree into a graph with one cycle.

    The first union that returns False is the answer, because it is the first
    edge joining two already-connected nodes. Nodes are 1-indexed here, which
    is why the DSU is sized n + 1.
    """
    dsu = UnionFind(len(edges) + 1)
    for a, b in edges:
        if not dsu.union(a, b):
            return [a, b]
    return []


def valid_tree(n: int, edges: list[list[int]]) -> bool:
    """A graph is a tree iff it is connected and has exactly n - 1 edges.

    Check the edge count first — it is O(1) and rules out most inputs — then
    verify no edge closes a cycle. Together those two facts force
    connectivity, so no separate connectivity pass is needed.
    """
    if len(edges) != n - 1:
        return False

    dsu = UnionFind(n)
    return all(dsu.union(a, b) for a, b in edges)


CASES = [
    ((5, [(0, 1), (1, 2), (3, 4)]), 2),
    ((5, []), 5),
    ((5, [(0, 1), (1, 2), (2, 3), (3, 4)]), 1),
    ((1, []), 1),
]


def solve(n: int, edges: list[tuple[int, int]]) -> int:
    return count_components(n, edges)


def check() -> None:
    for args, expected in CASES:
        assert count_components(*args) == expected

    dsu = UnionFind(4)
    assert dsu.union(0, 1) is True
    assert dsu.union(1, 2) is True
    assert dsu.union(0, 2) is False  # already connected
    assert dsu.connected(0, 2) is True
    assert dsu.connected(0, 3) is False
    assert dsu.components == 2

    assert find_redundant_connection([[1, 2], [1, 3], [2, 3]]) == [2, 3]
    assert find_redundant_connection([[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]]) == [1, 4]

    assert valid_tree(5, [[0, 1], [0, 2], [0, 3], [1, 4]]) is True
    assert valid_tree(5, [[0, 1], [1, 2], [2, 3], [1, 3], [1, 4]]) is False
    assert valid_tree(4, [[0, 1], [2, 3]]) is False  # right edge count, disconnected
