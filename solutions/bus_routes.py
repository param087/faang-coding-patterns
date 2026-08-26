"""Bus Routes — LeetCode 815."""

from __future__ import annotations

from collections import defaultdict, deque

META = {
    "pattern": "shortest-paths",
    "insight": "Make the buses the nodes: one BFS hop is an entire route, so you search 500 routes rather than 10⁵ stops.",
    "time": "O(S) where S is the total number of stops across all routes",
    "space": "O(S)",
    "sections": [
        (
            "What it asks",
            """
`routes[i]` is the loop of stops that bus `i` drives, for ever. Starting on
foot at stop `source`, return the fewest **buses** you must board to reach
`target`, or −1.

Ask whether `source == target` is possible. It is, the answer is **0**, and it
holds even when that stop appears on no route at all — you are already there.
That single guard is a large share of the failing submissions.
""",
        ),
        (
            "The insight",
            """
The obvious graph — stops joined to stops — is wrong twice over.

Riding one bus from the 3rd stop of a route to its 90th stop costs **one**
bus, not 87 hops, so every route would have to become a clique. With
`sum(len(routes[i])) ≤ 10⁵`, a single route of 10⁵ stops is about 5·10⁹
edges. You cannot build that graph, let alone search it.

Invert it: **routes are the nodes**. Two routes are adjacent when they share a
stop, and boarding one costs 1. That is at most 500 nodes, every edge has the
same weight, so it is plain unweighted **BFS** — no Dijkstra, no weights.

You never materialise the route-to-route adjacency either. A
`stop -> [route ids]` map supplies it lazily: pop a stop, expand every
not-yet-ridden route through it, push all of that route's stops. Each route is
expanded once and each stop is queued once, so the whole search is O(S).
""",
        ),
        (
            "The two visited sets",
            """
Both marks matter, and they fail differently.

- **Routes ridden.** Without this, the BFS re-expands the same route from
  every one of its stops: cost becomes `Σ len(route)²`, which for one
  10⁵-stop route is 10¹⁰. This is the one that TLEs rather than returns a
  wrong answer, so it survives every small test you write.
- **Stops queued.** A stop shared by ten routes must be enqueued once.

The counter is the other place to be careful. `buses` is incremented *before*
a level is processed, because standing at `source` is zero buses and the first
expansion is your first boarding. Check `target` while walking a route's stops
and return immediately — waiting to pop it off the queue works too, but then
the level bookkeeping has to be exactly right.

Finally, if `source` or `target` appears on no route and they differ, the
answer is −1 before any search happens.
""",
        ),
    ],
}


def num_buses_to_destination(routes: list[list[int]], source: int, target: int) -> int:
    if source == target:
        return 0  # already there, even if this stop is on no route

    stop_to_routes: dict[int, list[int]] = defaultdict(list)
    for index, route in enumerate(routes):
        for stop in route:
            stop_to_routes[stop].append(index)

    if source not in stop_to_routes or target not in stop_to_routes:
        return -1

    ridden: set[int] = set()  # routes already expanded — the O(S) guarantee
    seen_stops = {source}
    queue = deque([source])
    buses = 0

    while queue:
        buses += 1  # everything popped this level is reached with `buses` boardings
        for _ in range(len(queue)):
            stop = queue.popleft()
            for index in stop_to_routes[stop]:
                if index in ridden:
                    continue
                ridden.add(index)
                for next_stop in routes[index]:
                    if next_stop == target:
                        return buses
                    if next_stop not in seen_stops:
                        seen_stops.add(next_stop)
                        queue.append(next_stop)

    return -1


CASES = [
    (([[1, 2, 7], [3, 6, 7]], 1, 6), 2),
    (([[7, 12], [4, 5, 15], [6], [15, 19], [9, 12, 13]], 15, 12), -1),
    (([[1, 2, 7]], 1, 1), 0),  # source == target, on a route
    (([[1, 2, 7]], 5, 5), 0),  # source == target, on no route at all
    (([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]], 1, 10), 1),  # one ride, however many stops
    (([[1, 2], [2, 3], [3, 4]], 1, 4), 3),  # forced three-bus chain
    (([[1, 2, 7], [3, 6, 7], [2, 3]], 1, 6), 2),  # a shortcut route exists but does not help
    (([[1, 2, 3]], 5, 3), -1),  # source unreachable on foot
    (([], 1, 2), -1),
]


def solve(routes: list[list[int]], source: int, target: int) -> int:
    return num_buses_to_destination([list(route) for route in routes], source, target)
