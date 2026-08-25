"""Minimum spanning tree — Kruskal and Prim.

"Connect everything for the least total cost." Both algorithms are greedy and
both are provably optimal by the cut property: for any way of splitting the
nodes into two groups, the cheapest edge crossing that split belongs to some
MST.

Kruskal is easier to write if you already have [union-find]. Prim is better on
dense graphs, and it is the one to use when the graph is implicit — points on
a plane, where every pair is an edge and materialising them all is wasteful.
"""

from __future__ import annotations

import heapq

from .union_find import UnionFind


def kruskal(n: int, edges: list[tuple[int, int, int]]) -> int:
    """Total weight of an MST, or -1 if the graph is disconnected.

    Sort every edge by weight and take it unless it closes a cycle. `union`
    returning False *is* the cycle test, which is why DSU and Kruskal are
    usually taught together.
    """
    dsu = UnionFind(n)
    total = 0
    used = 0

    for weight, a, b in sorted((w, a, b) for a, b, w in edges):
        if dsu.union(a, b):
            total += weight
            used += 1
            if used == n - 1:
                break  # a spanning tree has exactly n-1 edges

    return total if used == n - 1 or n <= 1 else -1


def prim(n: int, adjacency: dict[int, list[tuple[int, int]]]) -> int:
    """Total MST weight by growing one tree from node 0.

    Keep a heap of edges leaving the tree; repeatedly take the cheapest one
    that reaches somewhere new. Note the visited check happens on *pop*, not
    on push — an edge can be queued before its endpoint is absorbed by a
    cheaper route.
    """
    if n <= 1:
        return 0

    visited = {0}
    heap: list[tuple[int, int]] = [(w, b) for b, w in adjacency.get(0, ())]
    heapq.heapify(heap)
    total = 0

    while heap and len(visited) < n:
        weight, node = heapq.heappop(heap)
        if node in visited:
            continue  # reached more cheaply already
        visited.add(node)
        total += weight
        for neighbour, w in adjacency.get(node, ()):
            if neighbour not in visited:
                heapq.heappush(heap, (w, neighbour))

    return total if len(visited) == n else -1


def min_cost_connect_points(points: list[tuple[int, int]]) -> int:
    """Min Cost to Connect All Points — Prim on an implicit complete graph.

    Every pair of points is an edge, so materialising them is O(n²) edges and
    Kruskal would then sort them in O(n² log n). Prim computes the distances
    lazily and stays O(n² log n) without the memory — which is the reason to
    know Prim at all.
    """
    n = len(points)
    if n <= 1:
        return 0

    visited = [False] * n
    best = [float("inf")] * n
    best[0] = 0
    total = 0

    for _ in range(n):
        # Pick the unvisited node closest to the tree.
        u = min((i for i in range(n) if not visited[i]), key=lambda i: best[i])
        visited[u] = True
        total += int(best[u])
        ux, uy = points[u]
        for v in range(n):
            if not visited[v]:
                vx, vy = points[v]
                distance = abs(ux - vx) + abs(uy - vy)
                if distance < best[v]:
                    best[v] = distance

    return total


CASES = [
    (([(0, 0), (2, 2), (3, 10), (5, 2), (7, 0)],), 20),
    (([(3, 12), (-2, 5), (-4, 1)],), 18),
    (([(0, 0)],), 0),
    (([],), 0),
]


def solve(points: list[tuple[int, int]]) -> int:
    return min_cost_connect_points(points)


def check() -> None:
    for args, expected in CASES:
        assert min_cost_connect_points(*args) == expected

    edges = [(0, 1, 1), (1, 2, 2), (0, 2, 3)]
    assert kruskal(3, edges) == 3
    assert kruskal(3, [(0, 1, 1)]) == -1  # disconnected
    assert kruskal(1, []) == 0

    adjacency: dict[int, list[tuple[int, int]]] = {
        0: [(1, 1), (2, 3)],
        1: [(0, 1), (2, 2)],
        2: [(0, 3), (1, 2)],
    }
    assert prim(3, adjacency) == 3
    assert prim(1, {}) == 0
    assert prim(2, {0: []}) == -1
