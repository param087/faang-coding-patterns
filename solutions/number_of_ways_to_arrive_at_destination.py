"""Number of Ways to Arrive at Destination — LeetCode 1976."""

from __future__ import annotations

import heapq

META = {
    "pattern": "shortest-paths",
    "insight": "Carry a path count alongside the distance: a strict improvement overwrites the count, an exact tie adds to it.",
    "time": "O(E log V)",
    "space": "O(V + E)",
    "sections": [
        (
            "What it asks",
            """
Undirected weighted graph, all times ≥ 1. Count the routes from 0 to `n − 1`
whose total time equals the **minimum** possible, modulo 10⁹ + 7.

Ask whether "shortest" means fewest edges or least time (least time), and
whether times can be 0. That second question is not idle — the answer here is
no, and the algorithm below quietly depends on it.
""",
        ),
        (
            "The insight",
            """
Run Dijkstra and carry a second array, `ways[v]` = number of shortest routes to
`v`. Every relaxation lands in exactly one of three cases:

- `d + w < dist[v]` — a strictly better route. **Overwrite**: `dist[v] = d + w`
  and `ways[v] = ways[u]`. Every route counted before is now too slow, so the
  old count is discarded, not added to.
- `d + w == dist[v]` — an equally good route through a different predecessor.
  **Accumulate**: `ways[v] += ways[u]`, and do **not** push to the heap; the
  distance did not change, so there is nothing new to propagate.
- otherwise, ignore.

The recurrence is `ways[v] = Σ ways[u]` over all `u` on some shortest path into
`v`. Because that sum has no cycles in it — a shortest-path DAG is acyclic when
weights are positive — the count is well defined.

The correctness hinge, and the thing to say out loud: **`ways[u]` must be final
when `u` is popped.** Dijkstra guarantees `dist[u]` is final at pop time, and
with strictly positive weights every predecessor on a shortest path to `u` has
a strictly smaller distance, so it was popped earlier and has already
contributed. Allow a 0-weight edge and that argument collapses — two nodes tie
at the same distance and the pop order decides whether one sees the other's
count.

Push into the heap only on a strict improvement. Pushing on ties can revisit a
node after it is settled and double-count.
""",
        ),
        (
            "Follow-ups",
            """
- **"Why the modulus?"** Counts explode. A layered graph of `k` diamonds in
  series has 2^k shortest routes, so at `n = 200` the true count needs about
  100 bits. Take the modulus at every accumulation, not at the end.
- **"Longest shortest path"** or **"count paths with at most T time"** — both
  drop out of the same DAG. Once you have `dist[]`, keep only the edges with
  `dist[u] + w == dist[v]`, which is the shortest-path DAG, and run any DP you
  like over its topological order. Building that DAG explicitly is the cleaner
  answer when the follow-up asks for something other than a plain count.
- **"Zero-weight edges?"** The DAG construction above still works, because it
  is built after distances are final; the inline counting does not. That is the
  concrete reason to prefer the two-pass version if the constraint is relaxed.
- **Second-shortest count**: keep two distance/count pairs per node, the same
  shape as *Second Minimum Time to Reach Destination*.
""",
        ),
    ],
}

MOD = 10**9 + 7


def count_paths(n: int, roads: list[list[int]]) -> int:
    graph: list[list[tuple[int, int]]] = [[] for _ in range(n)]
    for u, v, time in roads:
        graph[u].append((v, time))
        graph[v].append((u, time))

    dist = [float("inf")] * n
    ways = [0] * n
    dist[0] = 0
    ways[0] = 1
    heap = [(0, 0)]

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:  # stale entry
            continue
        for v, time in graph[u]:
            candidate = d + time
            if candidate < dist[v]:
                dist[v] = candidate
                ways[v] = ways[u]  # overwrite: the old routes are now too slow
                heapq.heappush(heap, (candidate, v))
            elif candidate == dist[v]:
                ways[v] = (ways[v] + ways[u]) % MOD  # tie: accumulate, do not push

    return ways[n - 1]


CASES = [
    ((7, [[0, 6, 7], [0, 1, 2], [1, 2, 3], [1, 3, 3], [6, 3, 3], [3, 5, 1], [6, 5, 1],
          [2, 5, 1], [0, 4, 5], [4, 6, 2]]), 4),
    ((2, [[1, 0, 10]]), 1),
    # Two routes of equal length.
    ((3, [[0, 1, 1], [1, 2, 1], [0, 2, 2]]), 2),
    ((4, [[0, 1, 1], [0, 2, 1], [1, 3, 1], [2, 3, 1]]), 2),
    # Counts must survive being carried through a node with a unique successor.
    ((5, [[0, 1, 1], [0, 2, 1], [1, 3, 1], [2, 3, 1], [3, 4, 1]]), 2),
    # Two diamonds in series multiply: 2 x 2.
    ((7, [[0, 1, 1], [0, 2, 1], [1, 3, 1], [2, 3, 1], [3, 4, 1], [3, 5, 1],
          [4, 6, 1], [5, 6, 1]]), 4),
    # A near-miss route of length 6 must not be counted against the minimum of 5.
    ((4, [[0, 1, 1], [1, 3, 5], [0, 2, 2], [2, 3, 3]]), 1),
    # Destination unreachable.
    ((3, [[0, 1, 1]]), 0),
]


def solve(n: int, roads: list[list[int]]) -> int:
    return count_paths(n, [road[:] for road in roads])
