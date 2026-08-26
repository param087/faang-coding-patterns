"""Second Minimum Time to Reach Destination — LeetCode 2045."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "shortest-paths",
    "insight": "Every edge costs the same, so BFS the two smallest distinct edge counts, then convert an edge count to clock time in a separate pass.",
    "time": "O(V + E)",
    "space": "O(V + E)",
    "sections": [
        (
            "What it asks",
            """
An undirected connected graph, nodes 1..n. Every edge takes exactly `time` to
cross. Traffic lights at every node flip between green and red every `change`
minutes, in lockstep, starting green at minute 0; you may **arrive** during red
but may only **depart** during green. Return the second-smallest distinct total
time to get from 1 to n.

Two clarifications carry the problem. "Second minimum" means the second
distinct **value**, not the second-best path — ten different routes all taking
17 minutes count once. And the lights are synchronised and free of any per-node
offset, which is what makes waiting a pure function of the clock rather than of
where you are.
""",
        ),
        (
            "The insight",
            """
Separate the two halves. Because every edge costs the same, the graph is
**unweighted** — no heap, no Dijkstra. All you need is the number of edges.

**Half one: BFS for the two smallest distinct edge counts to `n`.** Keep
`d1[v]` and `d2[v]` and enqueue a node at most twice, once per level it can
legitimately occupy. The relaxation is:

```
cand < d1[v]           -> d1[v] = cand, enqueue
d1[v] < cand < d2[v]   -> d2[v] = cand, enqueue
```

The strict `d1[v] < cand` is what enforces *distinct*.

The wrong first answer here is "second minimum = shortest + 2, just walk one
edge back and forth". It is often true, and it is false whenever an odd cycle
gives a route one edge longer: on the graph `1-2, 2-3, 3-4, 1-4, 1-3`, the
shortest route to 4 is 1 edge and the second is **2** (`1→3→4`), not 3. The
back-and-forth bound is an upper bound, not the answer.

**Half two: turn an edge count into a clock reading.** Walk the edges one at a
time. Before each departure, if `(t // change)` is odd the light is red, so
wait until `(t // change + 1) * change`; then add `time`. The number of edges is
at most `2n`, so this loop is trivially cheap and is far easier to get right
than a closed form.

Note that waiting depends only on the clock, never on the node — which is
exactly why the two halves separate. Fold the light rule into the BFS and you
have invented a weighted graph for no reason.
""",
        ),
        (
            "Edge cases",
            """
- **Is `d2[n]` always defined?** Yes. The graph is connected with `n ≥ 2` and
  has no self-loops, so from any node you can step to a neighbour and back,
  giving a route of `d1[n] + 2` edges. There is always a second value; no
  `-1` branch is needed.
- **`d2` for node 1 itself** is 2, not 0 — the BFS discovers it naturally when a
  neighbour relaxes back. Do not seed `d2[1]`, and do not mark node 1 as
  finished after the first visit.
- **A node genuinely needs two enqueues.** A `visited` set, or enqueueing only
  on the `d1` branch, silently returns the first minimum. This is the bug that
  passes the sample.
- **Arriving during red is legal.** Only departure is blocked, so never pad the
  final arrival — the last edge lands whenever it lands.
- **`change` larger than the whole journey** means the light never turns red and
  the answer is just `edges × time`.
""",
        ),
    ],
}


def second_minimum(n: int, edges: list[list[int]], time: int, change: int) -> int:
    graph: list[list[int]] = [[] for _ in range(n + 1)]
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)

    infinity = float("inf")
    d1: list[float] = [infinity] * (n + 1)
    d2: list[float] = [infinity] * (n + 1)
    d1[1] = 0
    queue = deque([(1, 0)])

    while queue:
        node, steps = queue.popleft()
        for nxt in graph[node]:
            candidate = steps + 1
            if candidate < d1[nxt]:
                d1[nxt] = candidate
                queue.append((nxt, candidate))
            elif d1[nxt] < candidate < d2[nxt]:  # strict: the value must differ
                d2[nxt] = candidate
                queue.append((nxt, candidate))

    elapsed = 0
    for _ in range(int(d2[n])):
        if (elapsed // change) % 2 == 1:  # red light: wait for the next green window
            elapsed = (elapsed // change + 1) * change
        elapsed += time  # arriving during red is fine; only departing is not
    return elapsed


CASES = [
    ((5, [[1, 2], [1, 3], [1, 4], [3, 4], [4, 5]], 3, 5), 13),
    ((2, [[1, 2]], 3, 2), 11),
    ((2, [[1, 2]], 3, 5), 13),
    # An odd cycle makes the second minimum shortest + 1, not shortest + 2.
    ((4, [[1, 2], [2, 3], [3, 4], [1, 4], [1, 3]], 2, 3), 4),
    # One full red wait in the middle of a four-edge walk.
    ((3, [[1, 2], [2, 3]], 5, 10), 30),
    # change larger than the journey: the light is never red.
    ((5, [[1, 2], [1, 3], [1, 4], [3, 4], [4, 5]], 3, 1000), 9),
    # Only route is back and forth along a path.
    ((3, [[1, 2], [2, 3]], 1, 100), 4),
]


def solve(n: int, edges: list[list[int]], time: int, change: int) -> int:
    return second_minimum(n, [edge[:] for edge in edges], time, change)
