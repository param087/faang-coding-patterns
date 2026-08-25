"""Network Delay Time — LeetCode 743."""

from __future__ import annotations

import heapq
from collections import defaultdict

META = {
    "pattern": "shortest-paths",
    "insight": "The signal arrives when the LAST node receives it, so the answer is the maximum of the shortest distances.",
    "time": "O(E log V)",
    "space": "O(V + E)",
    "sections": [
        (
            "What it asks",
            """
A signal starts at node `k` and travels along directed edges with given
delays. Return the time for **every** node to receive it, or −1 if some node
cannot.

Ask: are weights non-negative (yes → Dijkstra); is the graph directed (yes);
what if a node is unreachable (−1); is it 1-indexed (yes, on LeetCode).
""",
        ),
        (
            "The reading error",
            """
The answer is the **maximum** of the shortest distances, not the sum and not
the distance to any particular node.

The signal has reached everywhere when the last node gets it. This is a
reading error rather than an algorithmic one, and it is the most common way
this problem is failed.
""",
        ),
        (
            "The insight",
            """
Single-source shortest paths with non-negative weights: **Dijkstra**.

Compute the shortest distance from `k` to every node, then take the maximum.
If any distance is still infinity, some node is unreachable → −1.
""",
        ),
        (
            "The stale-entry guard",
            """
`if d > dist[node]: continue` is the line interviewers ask about.

Textbook Dijkstra uses a priority queue with *decrease-key*. `heapq` has no
such operation, so instead of updating an existing entry we push a second,
better one and **skip the stale entry when it surfaces**. That is lazy
deletion.

The consequence: the heap can hold O(E) entries rather than O(V), so the bound
is O(E log E) — which is the same as O(E log V), since E ≤ V².

"Lazy deletion, because heapq can't decrease-key" is the complete answer.
""",
        ),
        (
            "Dry run",
            """
`times = [[2,1,1],[2,3,1],[3,4,1]], n = 4, k = 2`.

Distances from 2: node 1 at 1, node 3 at 1, node 4 at 2. Maximum → **2**.

Then drop the last edge and node 4 becomes unreachable → −1.
""",
        ),
        (
            "Follow-ups",
            """
- **Negative weights** — Dijkstra breaks, because it commits to a node the
  first time it is popped and a negative edge can invalidate that. Use
  Bellman-Ford.
- **A limit on the number of hops** — the constraint is now on *edges*, which
  is Bellman-Ford's natural unit. See Cheapest Flights Within K Stops.
- **All-pairs with small n** — Floyd-Warshall, O(V³), with `k` as the
  outermost loop.
""",
        ),
    ],
}


def network_delay_time(times: list[list[int]], n: int, k: int) -> int:
    adjacency: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for source, target, weight in times:
        adjacency[source].append((target, weight))

    dist: dict[int, float] = {}
    heap: list[tuple[float, int]] = [(0, k)]

    while heap:
        d, node = heapq.heappop(heap)
        if node in dist:
            continue  # already settled — this is a stale entry
        dist[node] = d
        for neighbour, weight in adjacency[node]:
            if neighbour not in dist:
                heapq.heappush(heap, (d + weight, neighbour))

    if len(dist) < n:
        return -1  # some node was never reached
    return int(max(dist.values()))  # the LAST arrival, not the sum


CASES = [
    (([[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2), 2),
    (([[1, 2, 1]], 2, 1), 1),
    (([[1, 2, 1]], 2, 2), -1),
    (([], 1, 1), 0),
    (([[1, 2, 1], [2, 3, 2], [1, 3, 4]], 3, 1), 3),
]


def solve(times: list[list[int]], n: int, k: int) -> int:
    return network_delay_time(times, n, k)
