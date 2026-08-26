"""Minimum Weighted Subgraph With the Required Paths — LeetCode 2203."""

from __future__ import annotations

import heapq

META = {
    "pattern": "shortest-paths",
    "insight": "Any valid subgraph is two paths meeting at a node plus a shared tail, so try every meeting node against three precomputed distances.",
    "time": "O(E log V)",
    "space": "O(V + E)",
    "sections": [
        (
            "What it asks",
            """
A directed weighted graph. Find the minimum total edge weight of a subgraph in
which `dest` is reachable from **both** `src1` and `src2`; −1 if impossible.

Ask whether shared edges are paid for once (yes — that is the whole problem;
otherwise it is two independent shortest paths) and whether the graph is
directed (yes, which is why one of the three searches runs backwards).
""",
        ),
        (
            "The insight",
            """
The wrong first answer is `dist(src1, dest) + dist(src2, dest)`. It double-pays
for every edge the two routes share, and on `n = 4` with `0→2 (1)`, `1→2 (1)`,
`2→3 (5)` it reports 12 when the answer is **7**.

The structural claim that fixes it: an optimal subgraph is always **two paths
that meet at some node `m`, plus one shared path from `m` to `dest`.** A
minimal such subgraph has no branching after the two routes converge — if they
split apart again you could delete one of the branches and still have both
sources reaching `dest`, contradicting minimality. So the shape is a "Y", and
`m` may be `src1`, `src2` or `dest` itself, which covers the degenerate cases
where the paths never really merge.

That leaves one unknown: which node is `m`. There are only `n` candidates, so
try all of them. For a fixed `m` the cost is

```
d1[m] + d2[m] + dr[m]
```

with `d1` distances from `src1`, `d2` from `src2`, and `dr` distances **to**
`dest` — computed by running Dijkstra from `dest` on the **reversed** graph.
Building that reversed adjacency list is the step people forget on a directed
graph; it is the difference between an O(E log V) solution and an O(V · E log V)
one that runs Dijkstra from every node.

Three Dijkstras and a linear scan. Keep unreachable entries at infinity and the
sum stays infinite, so the −1 case needs no special handling.
""",
        ),
        (
            "Edge cases",
            """
- **Overflow.** With `n = 10⁵` edges at weight up to 10⁵, a path can reach 10¹⁰.
  In Python that is free; in C++ or Java this is a `long long` problem and the
  interviewer is watching for it.
- **Infinity arithmetic.** `float("inf") + float("inf")` is fine, but if you use
  a sentinel like `10**9` instead, three of them sum to something that looks
  like a real answer. Use a true infinity or check reachability explicitly.
- **`src1 == src2`, or either source equal to `dest`.** All handled by the same
  scan — `d1[src1] = 0` and `dr[dest] = 0`, so the meeting node just lands on an
  endpoint.
- **Parallel edges with different weights**: the adjacency list keeps both and
  Dijkstra picks the cheaper. Do not deduplicate into a dict keyed by
  `(u, v)` unless you take the minimum.
- **Self-loops and zero weights** are harmless here; Dijkstra needs only
  non-negativity.
""",
        ),
    ],
}


def _dijkstra(graph: list[list[tuple[int, int]]], source: int, n: int) -> list[float]:
    dist: list[float] = [float("inf")] * n
    dist[source] = 0
    heap = [(0.0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in graph[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(heap, (d + w, v))
    return dist


def minimum_weight(n: int, edges: list[list[int]], src1: int, src2: int, dest: int) -> int:
    forward: list[list[tuple[int, int]]] = [[] for _ in range(n)]
    backward: list[list[tuple[int, int]]] = [[] for _ in range(n)]
    for u, v, w in edges:
        forward[u].append((v, w))
        backward[v].append((u, w))  # reversed, so one search gives distances TO dest

    from_src1 = _dijkstra(forward, src1, n)
    from_src2 = _dijkstra(forward, src2, n)
    to_dest = _dijkstra(backward, dest, n)

    # The two routes meet at some node; try every candidate.
    best = min(a + b + c for a, b, c in zip(from_src1, from_src2, to_dest, strict=True))
    return -1 if best == float("inf") else int(best)


CASES = [
    ((6, [[0, 2, 2], [0, 5, 6], [1, 0, 3], [1, 4, 5], [2, 1, 1], [2, 3, 3], [2, 3, 4],
          [3, 4, 2], [4, 5, 1]], 0, 1, 5), 9),
    # dest reachable from src2 only.
    ((3, [[0, 1, 1], [2, 1, 1]], 0, 1, 2), -1),
    ((3, [[0, 2, 1], [1, 2, 1]], 0, 1, 2), 2),
    # The shared 2->3 tail is paid once; summing two shortest paths gives 12.
    ((4, [[0, 2, 1], [1, 2, 1], [2, 3, 5]], 0, 1, 3), 7),
    # A meeting node in the middle beats meeting at dest (14 vs 24).
    ((5, [[0, 3, 2], [1, 3, 2], [3, 4, 10], [0, 4, 100], [1, 4, 100]], 0, 1, 4), 14),
    # src2 is already at dest, so it contributes nothing.
    ((2, [[1, 0, 3]], 1, 0, 0), 3),
    # Parallel edges of different weight.
    ((3, [[0, 2, 5], [0, 2, 1], [1, 2, 1]], 0, 1, 2), 2),
    # Directed edges point the wrong way.
    ((3, [[1, 0, 1], [2, 1, 1]], 0, 1, 2), -1),
]


def solve(n: int, edges: list[list[int]], src1: int, src2: int, dest: int) -> int:
    return minimum_weight(n, [edge[:] for edge in edges], src1, src2, dest)
