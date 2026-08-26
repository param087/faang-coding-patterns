"""Reachable Nodes In Subdivided Graph — LeetCode 882."""

from __future__ import annotations

import heapq

META = {
    "pattern": "shortest-paths",
    "insight": "Never build the subdivided graph: Dijkstra the original nodes, then count each edge's new nodes from the leftover budget at both ends.",
    "time": "O(E log V)",
    "space": "O(V + E)",
    "sections": [
        (
            "What it asks",
            """
An undirected graph where edge `(u, v, cnt)` is replaced by a chain of `cnt`
brand-new nodes between `u` and `v`. Starting at node 0 with `maxMoves` moves,
count how many nodes of the subdivided graph you can reach — original nodes and
new ones together.

Ask what "reach" means: a node counts if it is within `maxMoves`, and you do
**not** have to stop there or come back. That is what allows the two ends of an
edge to be counted independently.
""",
        ),
        (
            "The insight",
            """
The subdivided graph is too big to build: `cnt` goes up to 10⁴ and there are up
to 10⁴ edges, so materialising it is 10⁸ nodes. But you never need it.

Two observations do the whole job.

**Original nodes.** Crossing edge `(u, v, cnt)` costs `cnt + 1` moves. That is
the only weight that matters, so run Dijkstra on the original graph — at most
3000 nodes — and every node with `dist[i] <= maxMoves` counts.

**Subdivided nodes, edge by edge.** For edge `(u, v, cnt)` you can walk
`a = maxMoves - dist[u]` of its new nodes inwards from `u`, and
`b = maxMoves - dist[v]` inwards from `v` (each clamped at 0). These are two
separate walks — you are not required to traverse the edge — so the count is

```
min(cnt, a + b)
```

The `min` is the line the problem is built around. When `a + b >= cnt` the
walks overlap and you would otherwise count some of the chain twice; capping at
`cnt` is exact, because overlap can only ever mean "the whole chain is
covered". Drop the `min` and every test with a short, well-connected edge
overcounts.

Clamping at 0 matters just as much: an unreachable endpoint contributes 0, not
a negative number that silently cancels the reachable end's contribution.

Total: reachable originals + Σ min(cnt, a + b) over all edges.
""",
        ),
        (
            "Follow-ups",
            """
- **"Why does Dijkstra on the original graph suffice?"** Because the new nodes
  are degree-2: a shortest path through the chain has no choices in it, so
  collapsing each chain to a single weight `cnt + 1` loses nothing. Say this
  explicitly — it is the justification for not building the graph, and it is
  what the question is testing.
- **"What if the new nodes had their own edges?"** Then the collapse is invalid
  and you are back to a genuinely large graph; the answer becomes bidirectional
  or A* search rather than a reformulation.
- **"Return the reachable set, not the count."** The count is a closed form over
  edges; the set is Θ(answer) and can be 10⁸ elements. Push back on the
  requirement before writing it.
- **Off-by-one check**: an edge with `cnt = 0` is a plain edge of weight 1 and
  contributes no extra nodes, which `min(0, a + b) = 0` handles for free.
""",
        ),
    ],
}


def reachable_nodes(edges: list[list[int]], max_moves: int, n: int) -> int:
    graph: list[list[tuple[int, int]]] = [[] for _ in range(n)]
    for u, v, cnt in edges:
        graph[u].append((v, cnt + 1))  # crossing the chain costs cnt + 1 moves
        graph[v].append((u, cnt + 1))

    dist: list[float] = [float("inf")] * n
    dist[0] = 0
    heap = [(0.0, 0)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in graph[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(heap, (d + w, v))

    total = sum(1 for d in dist if d <= max_moves)
    for u, v, cnt in edges:
        from_u = max(0, max_moves - dist[u])  # unreachable end clamps to 0
        from_v = max(0, max_moves - dist[v])
        total += min(cnt, from_u + from_v)  # the min stops double-counting overlap
    return int(total)


CASES = [
    (([[0, 1, 10], [0, 2, 1], [1, 2, 2]], 6, 3), 13),
    (([[0, 1, 4], [1, 2, 6], [0, 2, 8], [1, 3, 1]], 10, 4), 23),
    # Node 0 is isolated from the rest.
    (([[1, 2, 4], [1, 4, 5], [1, 3, 1], [4, 3, 5], [2, 4, 1]], 17, 5), 1),
    # Budget covers the whole chain from both ends: the min must cap it at 10.
    (([[0, 1, 10]], 20, 2), 12),
    # Budget runs out mid-chain and the far end is unreachable.
    (([[0, 1, 10]], 3, 2), 4),
    (([[0, 1, 5]], 0, 2), 1),
    (([], 5, 1), 1),
    # cnt = 0 edges add no new nodes.
    (([[0, 1, 0], [1, 2, 0]], 2, 3), 3),
]


def solve(edges: list[list[int]], max_moves: int, n: int) -> int:
    return reachable_nodes([edge[:] for edge in edges], max_moves, n)
