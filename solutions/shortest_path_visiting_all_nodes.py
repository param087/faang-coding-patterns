"""Shortest Path Visiting All Nodes — LeetCode 847."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "shortest-paths",
    "insight": "n ≤ 12 is the algorithm: BFS over (current node, bitmask of nodes seen), seeded from every node at once.",
    "time": "O(2ⁿ · n²)",
    "space": "O(2ⁿ · n)",
    "sections": [
        (
            "What it asks",
            """
An undirected, connected graph on `n ≤ 12` nodes, given as adjacency lists.
Return the length of the shortest walk that touches every node. You may start
anywhere, stop anywhere, and revisit nodes and edges as often as you like.

That freedom is the whole problem. Because revisits are allowed and no start
is fixed, this is **not** a Hamiltonian path question and the answer can
exceed `n − 1`: a star with three leaves needs 4 edges, not 3.
""",
        ),
        (
            "The insight",
            """
`n ≤ 12` is not a constraint, it is the algorithm. `2¹² = 4096`, so "which
nodes have I already seen" fits in a single integer and the entire state space
is `12 · 4096 = 49 152` states — you can afford to visit all of them.

State = `(node, mask)`. Every edge costs 1, so **BFS** over that state graph,
and the first time you pop a state with `mask == (1 << n) - 1` the current
level is the answer. No Dijkstra, no subset DP required.

Two details decide it:

- **Seed the queue with all `n` states `(i, 1 << i)` at distance 0.** The
  start is free, so this is a multi-source BFS. Running BFS once per start and
  taking the minimum is also correct, and `n` times slower for nothing.
- **Dedupe on the pair `(node, mask)`, never on `node` alone.** Revisiting a
  node is legitimate — it is exactly how you traverse a star — but returning
  to it with the *same* set already seen can never help. That pair is what
  keeps a walk-with-revisits search finite.

A mask only ever grows along an edge (`mask | 1 << next`), which is why the
state count stays at `2ⁿ · n` rather than blowing up with path length.
""",
        ),
        (
            "Follow-ups",
            """
- **Weighted edges.** Same state graph, swap BFS for Dijkstra over
  `(node, mask)`. Or run Floyd–Warshall for all-pairs distances first and then
  Held–Karp on the `2ⁿ · n` table — the classic TSP framing, of which this
  problem is the unweighted, open-tour, revisits-allowed cousin.
- **Must return to the start.** Fix the source instead of seeding all `n`, and
  close the tour by adding the distance back from the final node.
- **Disconnected input.** The queue drains without ever reaching the full
  mask, so a trailing `−1` is the honest return even though LeetCode
  guarantees connectivity.
- **How far does the bitmask stretch?** `n = 20` is `20 · 2²⁰ ≈ 2·10⁷`
  states — still fine. Around `n = 40` it dies and you are into heuristics.
""",
        ),
    ],
}


def shortest_path_length(graph: list[list[int]]) -> int:
    n = len(graph)
    if n <= 1:
        return 0

    full = (1 << n) - 1
    # Multi-source: the start is free, so every node begins at distance 0.
    queue = deque((node, 1 << node) for node in range(n))
    seen = {(node, 1 << node) for node in range(n)}
    steps = 0

    while queue:
        for _ in range(len(queue)):
            node, mask = queue.popleft()
            if mask == full:
                return steps
            for nxt in graph[node]:
                state = (nxt, mask | (1 << nxt))  # dedupe on the pair, not the node
                if state not in seen:
                    seen.add(state)
                    queue.append(state)
        steps += 1

    return -1  # only reachable if the graph is disconnected


CASES = [
    (([[1, 2, 3], [0], [0], [0]],), 4),  # star: 3 edges is impossible, must backtrack
    # Tree, hub at 1, three leaves: 2·edges − diameter = 2·5 − 4 = 6.
    (([[1], [0, 2, 4], [1, 3], [2], [1, 5], [4]],), 6),
    (([[1], [0]],), 1),
    (([[]],), 0),  # single node, already done
    (([],), 0),
    (([[1], [0, 2], [1, 3], [2]],), 3),  # path graph: n - 1 suffices
    (([[1, 2], [0, 2], [0, 1]],), 2),  # triangle
    (([[1, 2], [0], [0, 3], [2]],), 3),  # path 1-0-2-3, but node 0 is the middle
]


def solve(graph: list[list[int]]) -> int:
    return shortest_path_length([list(adj) for adj in graph])
