"""Path with Maximum Probability — LeetCode 1514."""

from __future__ import annotations

import heapq

META = {
    "pattern": "shortest-paths",
    "insight": "Probabilities only shrink when multiplied, so 'largest product first' obeys the same greedy argument as Dijkstra's 'smallest sum first'.",
    "time": "O(E log V)",
    "space": "O(V + E)",
    "sections": [
        (
            "What it asks",
            """
An undirected graph where each edge carries a success probability. Return the
highest probability of getting from `start` to `end` by multiplying the edge
probabilities along a path; 0 if no path exists.

Ask whether probabilities can be 0 (yes — an edge that always fails, which is
the same as no edge), and what tolerance the grader uses (1e-5, which matters
for the follow-up below).
""",
        ),
        (
            "The insight",
            """
Dijkstra, with two swaps: **maximise instead of minimise**, and **multiply
instead of add**.

The greedy argument survives intact, and that is the thing to say out loud.
Dijkstra needs each edge to make a path no better — with non-negative weights,
extending a path can only increase its sum. Here every probability lies in
`[0, 1]`, so extending a path can only *decrease* its product. Same
monotonicity, opposite direction. Pop the largest product first and the node is
settled.

`heapq` is a min-heap, so push `-probability`. Keep the stale-entry guard
(`if p < best[node]: continue`) for the same reason as ordinary Dijkstra: no
decrease-key, so improvements are pushed as fresh entries.

Returning the moment `end` is popped is safe and skips the rest of the graph.

The wrong first answer is greedy edge-picking: always walk the strongest edge
out of the current node. On `0→1` at 0.9 then `1→3` at 0.1 versus `0→2` at 0.5
then `2→3` at 0.9, greedy takes 0.09 and the answer is 0.45.
""",
        ),
        (
            "The log trick, and why not to use it",
            """
The obvious reflex is `-log(p)`, turning products into sums so you can run
stock Dijkstra unmodified. It is correct, and worth naming in an interview
because it shows you see the isomorphism.

Do not actually write it. `log(0)` is a domain error you now have to special-case,
and summing 10⁴ logs accumulates float error in a way that a running product
does not — the product underflows towards 0 gracefully, whereas the log sum
drifts. With a 1e-5 tolerance, drift is the failure mode that bites.

Multiplying directly is shorter, has no special case, and is the same
algorithm. Mention the transform, write the product.
""",
        ),
    ],
}


def max_probability(
    n: int,
    edges: list[list[int]],
    succ_prob: list[float],
    start_node: int,
    end_node: int,
) -> float:
    graph: list[list[tuple[int, float]]] = [[] for _ in range(n)]
    for (u, v), p in zip(edges, succ_prob, strict=True):
        graph[u].append((v, p))
        graph[v].append((u, p))

    best = [0.0] * n
    best[start_node] = 1.0
    heap = [(-1.0, start_node)]  # heapq is a min-heap; negate to pop the largest

    while heap:
        negated, node = heapq.heappop(heap)
        probability = -negated
        if node == end_node:
            return probability
        if probability < best[node]:  # stale entry, superseded by a better push
            continue
        for neighbour, edge_p in graph[node]:
            candidate = probability * edge_p
            if candidate > best[neighbour]:
                best[neighbour] = candidate
                heapq.heappush(heap, (-candidate, neighbour))

    return 0.0


CASES = [
    ((3, [[0, 1], [1, 2], [0, 2]], [0.5, 0.5, 0.2], 0, 2), 0.25),
    ((3, [[0, 1], [1, 2], [0, 2]], [0.5, 0.5, 0.3], 0, 2), 0.3),
    ((3, [[0, 1]], [0.5], 0, 2), 0.0),
    ((1, [], [], 0, 0), 1.0),
    # Greedy "take the strongest edge" answers 0.09.
    ((4, [[0, 1], [0, 2], [1, 3], [2, 3]], [0.9, 0.5, 0.1, 0.9], 0, 3), 0.45),
    # Four weak-ish hops beat one strong shortcut.
    ((5, [[0, 1], [1, 2], [2, 3], [3, 4], [0, 4]], [0.9, 0.9, 0.9, 0.9, 0.6], 0, 4), 0.6561),
    # A zero-probability edge is an edge that is not there.
    ((4, [[0, 1], [1, 3], [0, 2], [2, 3]], [1.0, 0.0, 0.5, 0.5], 0, 3), 0.25),
]


def solve(
    n: int,
    edges: list[list[int]],
    succ_prob: list[float],
    start_node: int,
    end_node: int,
) -> float:
    # Rounded to the grader's 1e-5 tolerance so cases compare exactly.
    return round(max_probability(n, edges, succ_prob, start_node, end_node), 5)
