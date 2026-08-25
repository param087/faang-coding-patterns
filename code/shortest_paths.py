"""Shortest paths on weighted graphs.

Pick by the constraint, not by habit:

    non-negative weights, one source     Dijkstra        O(E log V)
    negative weights allowed             Bellman-Ford    O(V·E)
    all pairs, small V                   Floyd-Warshall  O(V^3)
    at most k edges                      Bellman-Ford    O(k·E)
    unweighted                           BFS             O(V + E)

Reaching for Dijkstra on a graph with negative edges is the classic mistake:
it commits to a node the first time it is popped, and a negative edge can
later invalidate that.
"""

from __future__ import annotations

import heapq
from collections import defaultdict


def dijkstra(n: int, edges: list[tuple[int, int, int]], source: int) -> list[float]:
    """Shortest distance from source to every node; inf if unreachable.

    Lazy deletion is the detail worth knowing. `heapq` cannot decrease a key,
    so instead of updating an entry we push a second, better one and skip
    stale pops with the `> dist[node]` guard. The heap may hold O(E) entries,
    which is why the bound is O(E log E) — the same thing as O(E log V).
    """
    adjacency: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for a, b, weight in edges:
        adjacency[a].append((b, weight))

    dist: list[float] = [float("inf")] * n
    dist[source] = 0
    heap: list[tuple[float, int]] = [(0, source)]

    while heap:
        d, node = heapq.heappop(heap)
        if d > dist[node]:
            continue  # stale entry, superseded by a shorter path
        for neighbour, weight in adjacency[node]:
            candidate = d + weight
            if candidate < dist[neighbour]:
                dist[neighbour] = candidate
                heapq.heappush(heap, (candidate, neighbour))

    return dist


def bellman_ford(
    n: int, edges: list[tuple[int, int, int]], source: int
) -> list[float] | None:
    """Shortest distances allowing negative weights; None on a negative cycle.

    Relax every edge n-1 times — that is enough because a shortest path has at
    most n-1 edges. An n-th round that still improves something proves a
    negative cycle exists.
    """
    dist: list[float] = [float("inf")] * n
    dist[source] = 0

    for _ in range(n - 1):
        changed = False
        for a, b, weight in edges:
            if dist[a] + weight < dist[b]:
                dist[b] = dist[a] + weight
                changed = True
        if not changed:
            break  # settled early

    for a, b, weight in edges:
        if dist[a] + weight < dist[b]:
            return None  # still improving: negative cycle

    return dist


def cheapest_flights_within_k_stops(
    n: int, flights: list[list[int]], source: int, target: int, k: int
) -> int:
    """Cheapest source→target route using at most k intermediate stops.

    The reason this is Bellman-Ford and not Dijkstra: the constraint is on the
    *number of edges*, and Bellman-Ford's rounds are exactly edge counts. The
    snapshot copy is essential — relaxing from an array you are also writing
    lets a single round use two edges, silently allowing k+1 stops.
    """
    dist: list[float] = [float("inf")] * n
    dist[source] = 0

    for _ in range(k + 1):
        snapshot = dist[:]  # relax from the previous round only
        for a, b, price in flights:
            if snapshot[a] + price < dist[b]:
                dist[b] = snapshot[a] + price

    return -1 if dist[target] == float("inf") else int(dist[target])


def floyd_warshall(n: int, edges: list[tuple[int, int, int]]) -> list[list[float]]:
    """All-pairs shortest paths in O(V^3).

    The loop order is not negotiable: `k` must be outermost. It reads as
    "allowing paths through the first k nodes", and any other nesting computes
    something that is not shortest paths.
    """
    dist: list[list[float]] = [[float("inf")] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0
    for a, b, weight in edges:
        dist[a][b] = min(dist[a][b], weight)

    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    return dist


def network_delay_time(times: list[list[int]], n: int, k: int) -> int:
    """Time for a signal from node k to reach every node, or -1."""
    dist = dijkstra(n, [(a - 1, b - 1, w) for a, b, w in times], k - 1)
    longest = max(dist)
    return -1 if longest == float("inf") else int(longest)


CASES = [
    (([[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2), 2),
    (([[1, 2, 1]], 2, 1), 1),
    (([[1, 2, 1]], 2, 2), -1),
]


def solve(times: list[list[int]], n: int, k: int) -> int:
    return network_delay_time(times, n, k)


def check() -> None:
    for args, expected in CASES:
        assert network_delay_time(*args) == expected

    dist = dijkstra(4, [(0, 1, 1), (1, 2, 2), (0, 2, 5), (2, 3, 1)], 0)
    assert dist == [0, 1, 3, 4]  # 0->1->2 beats the direct 0->2
    assert dijkstra(2, [], 0) == [0, float("inf")]

    assert bellman_ford(3, [(0, 1, 1), (1, 2, -2)], 0) == [0, 1, -1]
    assert bellman_ford(2, [(0, 1, 1), (1, 0, -3)], 0) is None  # negative cycle

    flights = [[0, 1, 100], [1, 2, 100], [0, 2, 500]]
    assert cheapest_flights_within_k_stops(3, flights, 0, 2, 1) == 200
    assert cheapest_flights_within_k_stops(3, flights, 0, 2, 0) == 500

    all_pairs = floyd_warshall(3, [(0, 1, 1), (1, 2, 2)])
    assert all_pairs[0][2] == 3
    assert all_pairs[2][0] == float("inf")
